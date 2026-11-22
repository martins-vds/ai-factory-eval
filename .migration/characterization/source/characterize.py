import argparse
import difflib
import json
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from urllib import error, parse, request

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'legacy'
RUN_SCRIPT = SOURCE / 'run.sh'
GRAPH = ROOT / '.migration/graphs/source/full/knowledge-graph.json'
GOLDENS = ROOT / '.migration/characterization/source/goldens'
BASE_URL = 'http://127.0.0.1:8080'
CASES = (
    ('GET /about', 'GET', '/about', None),
    ('POST /payments/{id}', 'POST', '/payments/L3', None),
    ('GET /fees/{id}', 'GET', '/fees/L3', None),
    ('GET /loans', 'GET', '/loans', None),
    ('GET /loans/{id}', 'GET', '/loans/L1', None),
    ('POST /loans', 'POST', '/loans', {'member': 'dee', 'isbn': '123'}),
    ('POST /loans/{id}/return', 'POST', '/loans/L1/return', None),
)
EDGE_CASES = (
    ('GET /fees/L1 (unreturned)', 'GET', '/fees/L1', None),
    ('GET /fees/L2 (early return)', 'GET', '/fees/L2', None),
    ('GET /fees/unknown', 'GET', '/fees/unknown', None),
    ('GET /loans/unknown', 'GET', '/loans/unknown', None),
    ('POST /loans (missing member)', 'POST', '/loans', {'isbn': 'missing-member'}),
    ('POST /loans (missing isbn)', 'POST', '/loans', {'member': 'missing-isbn'}),
    ('POST /loans (empty member)', 'POST', '/loans', {'member': '', 'isbn': 'empty-member'}),
    ('POST /loans (empty isbn)', 'POST', '/loans', {'member': 'empty-isbn', 'isbn': ''}),
    (
        'POST /loans (semicolon member)',
        'POST',
        '/loans',
        {'member': 'gray;lee', 'isbn': 'semicolon'},
    ),
    ('POST /loans/L2/return', 'POST', '/loans/L2/return', None),
    ('POST /loans/L2/return (repeat)', 'POST', '/loans/L2/return', None),
    ('POST /loans/unknown/return', 'POST', '/loans/unknown/return', None),
    ('POST /payments/L1', 'POST', '/payments/L1', None),
    ('POST /payments/L1 (repeat)', 'POST', '/payments/L1', None),
    ('POST /payments/L2 (gateway status)', 'POST', '/payments/L2', None),
    ('POST /payments/unknown', 'POST', '/payments/unknown', None),
)


class GatewayHandler(BaseHTTPRequestHandler):
    requests: ClassVar[list[dict[str, str]]] = []

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        loan_id = parse.parse_qs(parse.urlsplit(self.path).query).get('loan', [''])[0]
        self.requests.append({'method': 'POST', 'path': self.path, 'body': body.decode('utf-8')})
        if loan_id == 'L3':
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()
            return
        status, response_body = (
            (503, 'gateway failure\n') if loan_id == 'L2' else (200, 'charged\n')
        )
        encoded = response_body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, _format, *args):
        pass


def verify_graph_coverage():
    graph = json.loads(GRAPH.read_text(encoding='utf-8'))
    endpoints = {node['name'] for node in graph['nodes'] if node.get('type') == 'endpoint'}
    covered = {case[0] for case in CASES}
    if endpoints != covered:
        missing = sorted(endpoints - covered)
        unexpected = sorted(covered - endpoints)
        raise RuntimeError(f'graph endpoint mismatch; missing={missing}, unexpected={unexpected}')


def get_response(method, path, form):
    body = parse.urlencode(form).encode() if form is not None else None
    headers = {'Content-Type': 'application/x-www-form-urlencoded'} if body is not None else {}
    req = request.Request(f'{BASE_URL}{path}', data=body, headers=headers, method=method)
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


def wait_until_ready(process, output):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output.seek(0)
            raise RuntimeError(
                f'legacy app exited early:\n{output.read().decode(errors="replace")[-4000:]}'
            )
        try:
            with request.urlopen(f'{BASE_URL}/about', timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, error.URLError):
            time.sleep(0.5)
    raise TimeoutError('legacy app did not become ready at http://127.0.0.1:8080')


def exercise_http():
    observations = {}
    for endpoint, method, path, form in (*CASES, *EDGE_CASES):
        observations[endpoint] = {
            'request': {
                'method': method,
                'path': path,
                'form': form,
            },
            'response': get_response(method, path, form),
        }
    observations['GET /loans/L7'] = {
        'request': {'method': 'GET', 'path': '/loans/L7', 'form': None},
        'response': get_response('GET', '/loans/L7', None),
    }
    return observations


def exercise_browser():
    pages = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            for path in ('/about', '/fees/L3'):
                response = page.goto(f'{BASE_URL}{path}', wait_until='domcontentloaded')
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


def normalize(observation, endpoint):
    response = observation['response']
    body = re.sub(r'\d{4}-\d{2}-\d{2}', '<date>', response['body'])
    if endpoint.startswith('GET /fees/'):
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
        actual = {
            key: normalize(value, key) if 'response' in value else value
            for key, value in observation.items()
        }
        baseline = {
            key: normalize(value, key) if 'response' in value else value
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
    gateway = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    gateway_thread = threading.Thread(target=gateway.serve_forever, daemon=True)
    gateway_thread.start()
    GatewayHandler.requests = []
    env = os.environ.copy()
    env.pop('PORT', None)
    env['PAYMENT_GATEWAY_URL'] = f'http://127.0.0.1:{gateway.server_port}'
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            ['bash', str(RUN_SCRIPT)],
            cwd=SOURCE,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            wait_until_ready(process, output)
            http = exercise_http()
            browser = exercise_browser()
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            ['bash', str(RUN_SCRIPT)],
            cwd=SOURCE,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            wait_until_ready(process, output)
            http['GET /loans after restart'] = {
                'request': {'method': 'GET', 'path': '/loans', 'form': None},
                'response': get_response('GET', '/loans', None),
            }
            http['GET /loans/L4 after restart'] = {
                'request': {'method': 'GET', 'path': '/loans/L4', 'form': None},
                'response': get_response('GET', '/loans/L4', None),
            }
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    gateway.shutdown()
    gateway.server_close()
    gateway_thread.join()
    http['application lifecycle'] = {
        'command': 'legacy/run.sh',
        'port': 'default 8080',
        'startup_ready': True,
        'shutdown_completed': True,
        'restart_reseeds_database': True,
    }
    write_or_compare('http', http, args.record)
    write_or_compare('gateway', GatewayHandler.requests, args.record)
    write_or_compare('browser', browser, args.record)
    action = 'recorded' if args.record else 'verified'
    print(
        f'{action} {len(CASES)} source graph endpoints, '
        f'{len(http) - len(CASES) - 1} additional HTTP cases, '
        f'{len(GatewayHandler.requests)} gateway calls, and {len(browser["pages"])} browser pages'
    )


if __name__ == '__main__':
    main()
