import argparse
import difflib
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import error, parse, request

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / '.source' / 'legacy'
GRAPH = ROOT / '.migration/graphs/source/full/knowledge-graph.json'
GOLDENS = ROOT / '.migration/characterization/source/goldens'
CASES = (
    ('GET /about', 'about', 'GET', '/about', None),
    ('GET /fees/{id}', 'fee-overdue', 'GET', '/fees/L1', None),
    ('GET /fees/{id}', 'fee-early-return', 'GET', '/fees/L2', None),
    ('GET /fees/{id}', 'fee-late-return', 'GET', '/fees/L3', None),
    ('GET /fees/{id}', 'fee-unknown-loan', 'GET', '/fees/unknown', None),
    ('GET /loans', 'seeded-loans', 'GET', '/loans', None),
    ('GET /loans/{id}', 'known-loan', 'GET', '/loans/L1', None),
    ('GET /loans/{id}', 'unknown-loan', 'GET', '/loans/unknown', None),
    ('POST /loans', 'lend-valid', 'POST', '/loans', {'member': 'dee', 'isbn': '123'}),
    ('POST /loans', 'lend-missing-isbn', 'POST', '/loans', {'member': 'dee'}),
    ('POST /loans', 'lend-missing-member', 'POST', '/loans', {'isbn': '123'}),
    ('POST /loans', 'lend-empty-fields', 'POST', '/loans', {'member': '', 'isbn': ''}),
    ('GET /loans', 'loans-after-lending', 'GET', '/loans', None),
    ('POST /loans/{id}/return', 'return-known-loan', 'POST', '/loans/L1/return', None),
    ('POST /loans/{id}/return', 'return-already-returned-loan', 'POST', '/loans/L2/return', None),
    ('POST /loans/{id}/return', 'return-unknown-loan', 'POST', '/loans/unknown/return', None),
    ('POST /payments/{id}', 'payment-unknown-loan', 'POST', '/payments/unknown', None),
    ('POST /payments/{id}', 'payment-unavailable-gateway', 'POST', '/payments/L3', None),
)
CASE_ENDPOINTS = {label: endpoint for endpoint, label, *_ in CASES}


def verify_graph_coverage():
    graph = json.loads(GRAPH.read_text(encoding='utf-8'))
    endpoints = {node['name'] for node in graph['nodes'] if node.get('type') == 'endpoint'}
    covered = {case[0] for case in CASES}
    if endpoints != covered:
        missing = sorted(endpoints - covered)
        unexpected = sorted(covered - endpoints)
        raise RuntimeError(f'graph endpoint mismatch; missing={missing}, unexpected={unexpected}')


def get_response(base_url, method, path, form):
    body = parse.urlencode(form).encode() if form is not None else None
    headers = {'Content-Type': 'application/x-www-form-urlencoded'} if body is not None else {}
    req = request.Request(f'{base_url}{path}', data=body, headers=headers, method=method)
    try:
        response = request.urlopen(req, timeout=10)
    except error.HTTPError as exc:
        response = exc
    with response:
        return {
            'status': response.status,
            'content_type': response.headers.get('Content-Type'),
            'body': response.read().decode('utf-8'),
        }


def wait_until_ready(process, output, base_url):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output.seek(0)
            raise RuntimeError(
                f'legacy app exited early:\n{output.read().decode(errors="replace")[-4000:]}'
            )
        try:
            with request.urlopen(f'{base_url}/about', timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, error.URLError):
            time.sleep(0.5)
    raise TimeoutError(f'legacy app did not become ready at {base_url}')


def exercise_http(base_url):
    observations = {}
    for endpoint, label, method, path, form in CASES:
        observations[label] = {
            'request': {
                'method': method,
                'path': path,
                'form': form,
            },
            'response': get_response(base_url, method, path, form),
        }
    return observations


def exercise_browser(base_url):
    pages = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            for path in ('/about', '/fees/L3'):
                response = page.goto(f'{base_url}{path}', wait_until='domcontentloaded')
                if response is None:
                    raise RuntimeError(f'browser navigation returned no response for {path}')
                pages.append(
                    {
                        'path': path,
                        'status': response.status,
                        'heading': page.locator('h1').inner_text(),
                    }
                )
        finally:
            browser.close()
    return {'pages': pages}


def available_port():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        return listener.getsockname()[1]


def stop_process(process):
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def exercise_gateway(source_copy):
    gateway_requests = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            size = int(self.headers.get('Content-Length', '0'))
            gateway_requests.append(
                {'method': self.command, 'path': self.path, 'body': self.rfile.read(size).decode()}
            )
            loan_id = parse.parse_qs(parse.urlsplit(self.path).query).get('loan', [''])[0]
            status, body = (200, 'charged\n') if loan_id == 'L3' else (402, 'declined\n')
            self.send_response(status)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, format, *args):
            pass

    gateway = HTTPServer(('127.0.0.1', 0), GatewayHandler)
    threading.Thread(target=gateway.serve_forever, daemon=True).start()
    gateway_url = f'http://127.0.0.1:{gateway.server_port}'
    port = available_port()
    base_url = f'http://127.0.0.1:{port}'
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['PAYMENT_GATEWAY_URL'] = gateway_url
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            ['java', '-cp', 'target/classes:target/dependency/*', 'lib.App'],
            cwd=source_copy,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            wait_until_ready(process, output, base_url)
            observations = {'fresh-start-loans': get_response(base_url, 'GET', '/loans', None)}
            for label, loan_id in (('gateway-success', 'L3'), ('gateway-error', 'L2')):
                response = get_response(base_url, 'POST', f'/payments/{loan_id}', None)
                observations[label] = {
                    'gateway_request': gateway_requests[-1],
                    'response': response,
                }
        finally:
            stop_process(process)
            gateway.shutdown()
            gateway.server_close()
    return observations


def exercise_fee_boundaries(source_copy):
    today = date.today()
    due = today - timedelta(days=10)
    lent_on = due - timedelta(days=14)
    seed = source_copy / 'target/classes/META-INF/seed.sql'
    seed.chmod(seed.stat().st_mode | 0o200)
    with seed.open('a', encoding='utf-8') as output:
        for loan_id, days_late in (('L4', 2), ('L5', 3)):
            returned_on = due + timedelta(days=days_late)
            output.write(
                f"\nINSERT INTO LOAN (ID, MEMBER, ISBN, LENT_ON, RETURNED_ON) "
                f"VALUES ('{loan_id}', 'boundary', 'test', DATE '{lent_on}', "
                f"DATE '{returned_on}');\n"
            )
    port = available_port()
    base_url = f'http://127.0.0.1:{port}'
    env = os.environ.copy()
    env['PORT'] = str(port)
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            ['java', '-cp', 'target/classes:target/dependency/*', 'lib.App'],
            cwd=source_copy,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            wait_until_ready(process, output, base_url)
            return {
                f'{days_late}-days-late': {
                    'request': {'method': 'GET', 'path': f'/fees/{loan_id}', 'form': None},
                    'response': get_response(base_url, 'GET', f'/fees/{loan_id}', None),
                }
                for loan_id, days_late in (('L4', 2), ('L5', 3))
            }
        finally:
            stop_process(process)


def normalize(observation, endpoint, include_fee_details=True):
    response = observation['response']
    body = re.sub(r'\d{4}-\d{2}-\d{2}', '<date>', response['body'])
    if endpoint == 'GET /fees/{id}' and include_fee_details:
        body = re.sub(r'\d+ day\(s\) late', '<days> day(s) late', body)
        body = re.sub(r'Fee: \$\d+\.\d{2}', 'Fee: $<amount>', body)
    return {
        'request': observation['request'],
        'response': {
            'status': response['status'],
            'content_type': response['content_type'],
            'body': body,
        },
    }


def write_or_compare(name, observation, record):
    path = GOLDENS / f'{name}.json'
    rendered = json.dumps(observation, indent=2, sort_keys=True) + '\n'
    if record:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding='utf-8')
        return
    expected = json.loads(path.read_text(encoding='utf-8'))
    if name == 'http':
        actual = {key: normalize(value, CASE_ENDPOINTS[key]) for key, value in observation.items()}
        baseline = {key: normalize(value, CASE_ENDPOINTS[key]) for key, value in expected.items()}
    elif name == 'fee-boundaries':
        actual = {
            key: normalize(value, 'GET /fees/{id}', include_fee_details=False)
            for key, value in observation.items()
        }
        baseline = {
            key: normalize(value, 'GET /fees/{id}', include_fee_details=False)
            for key, value in expected.items()
        }
    else:
        actual = observation
        baseline = expected
    if actual != baseline:
        before = json.dumps(baseline, indent=2, sort_keys=True).splitlines()
        after = json.dumps(actual, indent=2, sort_keys=True).splitlines()
        diff = '\n'.join(difflib.unified_diff(before, after, fromfile=str(path), tofile='observed'))
        raise AssertionError(f'golden mismatch:\n{diff}')


def main():
    parser = argparse.ArgumentParser(
        description='Characterize the pinned legacy HTTP and browser behavior.'
    )
    parser.add_argument(
        '--record', action='store_true', help='write current observations to golden files'
    )
    args = parser.parse_args()
    verify_graph_coverage()
    with tempfile.TemporaryDirectory() as directory:
        source_copy = Path(directory) / 'legacy'
        shutil.copytree(SOURCE, source_copy)
        source_copy.chmod(source_copy.stat().st_mode | 0o700)
        env = os.environ.copy()
        env.pop('PORT', None)
        env.pop('PAYMENT_GATEWAY_URL', None)
        base_url = 'http://127.0.0.1:8080'
        with tempfile.TemporaryFile() as output:
            process = subprocess.Popen(
                ['bash', str(source_copy / 'run.sh')],
                cwd=source_copy,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
            )
            try:
                wait_until_ready(process, output, base_url)
                http = exercise_http(base_url)
                browser = exercise_browser(base_url)
            finally:
                stop_process(process)
        gateway = exercise_gateway(source_copy)
        fee_boundaries = exercise_fee_boundaries(source_copy)
    write_or_compare('http', http, args.record)
    write_or_compare('browser', browser, args.record)
    write_or_compare('gateway', gateway, args.record)
    write_or_compare('fee-boundaries', fee_boundaries, args.record)
    action = 'recorded' if args.record else 'verified'
    print(
        f'{action} {len(http)} HTTP cases across 7 endpoints, '
        f'{len(browser["pages"])} browser pages, {len(gateway) - 1} gateway cases, '
        f'and {len(fee_boundaries)} fee-boundary cases'
    )


if __name__ == '__main__':
    main()
