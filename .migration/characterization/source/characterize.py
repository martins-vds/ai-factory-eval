import argparse
import difflib
import json
import os
import re
import subprocess
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
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


def observe_http(method, path, form):
    return {
        'request': {
            'method': method,
            'path': path,
            'form': form,
        },
        'response': get_response(method, path, form),
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
    for endpoint, method, path, form in CASES:
        observations[endpoint] = observe_http(method, path, form)
    return observations


def start_gateway():
    observations = []

    class GatewayHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            observations.append({'method': 'POST', 'path': self.path, 'body': body.decode()})
            loan = parse.parse_qs(parse.urlsplit(self.path).query).get('loan', [''])[0]
            status, response_body = {
                'L1': (200, b'payment accepted\n'),
                'L2': (402, b'payment declined\n'),
                'L3': (503, b'payment gateway unavailable\n'),
            }.get(loan, (503, b'payment gateway unavailable\n'))
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        def log_message(self, format, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, observations, f'http://127.0.0.1:{server.server_port}'


def stop_gateway(server, thread):
    if server is not None:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def start_source(output, env):
    process = subprocess.Popen(
        ['bash', str(RUN_SCRIPT)],
        cwd=SOURCE,
        env=env,
        stdout=output,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_until_ready(process, output)
    except Exception:
        stop_source(process)
        raise
    return process


def stop_source(process):
    if process is None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def exercise_edge_cases():
    cases = (
        ('GET /loans/not-found', 'GET', '/loans/not-found', None),
        ('GET /fees/not-found', 'GET', '/fees/not-found', None),
        ('POST /loans/not-found/return', 'POST', '/loans/not-found/return', None),
        ('POST /payments/not-found', 'POST', '/payments/not-found', None),
        ('POST /loans missing both fields', 'POST', '/loans', {}),
        ('POST /loans missing member', 'POST', '/loans', {'isbn': '123'}),
        ('POST /loans missing ISBN', 'POST', '/loans', {'member': 'dee'}),
        ('POST /loans empty fields', 'POST', '/loans', {'member': '', 'isbn': ''}),
        (
            'POST /loans delimiter fields',
            'POST',
            '/loans',
            {'member': 'member;line\nbreak', 'isbn': 'isbn;value'},
        ),
        ('GET /fees/L2 before return', 'GET', '/fees/L2', None),
        ('POST /loans/L2/return repeated', 'POST', '/loans/L2/return', None),
        ('GET /loans/L2 after repeated return', 'GET', '/loans/L2', None),
        ('POST /payments/L1 gateway success', 'POST', '/payments/L1', None),
        ('POST /payments/L2 gateway rejection', 'POST', '/payments/L2', None),
    )
    return {name: observe_http(method, path, form) for name, method, path, form in cases}


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
        days = re.search(r'(\d+) day\(s\) late', body)
        if days:
            category = 'zero' if int(days.group(1)) == 0 else 'positive'
            body = re.sub(r'\d+ day\(s\) late', f'<{category}> day(s) late', body)
        fee = re.search(r'Fee: \$(\d+)\.(\d{2})', body)
        if fee:
            cents = int(fee.group(1)) * 100 + int(fee.group(2))
            category = 'zero' if cents == 0 else 'capped' if cents >= 1000 else 'positive'
            body = re.sub(r'Fee: \$\d+\.\d{2}', f'Fee: $<{category}>', body)
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
        actual = {key: normalize(value, key) for key, value in observation.items()}
        baseline = {key: normalize(value, key) for key, value in expected.items()}
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
    gateway = None
    gateway_thread = None
    process = None
    with tempfile.TemporaryFile() as output:
        try:
            gateway, gateway_thread, gateway_observations, gateway_url = start_gateway()
            env = os.environ.copy()
            env['PORT'] = '8080'
            env['PAYMENT_GATEWAY_URL'] = gateway_url
            process = start_source(output, env)
            http = {'GET /fees/L1 before return': observe_http('GET', '/fees/L1', None)}
            http.update(exercise_http())
            http.update(exercise_edge_cases())
            browser = exercise_browser()
            stop_gateway(gateway, gateway_thread)
            gateway = None
            http['POST /payments/L4 gateway unavailable'] = observe_http(
                'POST', '/payments/L4', None
            )
            stop_source(process)
            process = None
            restart_env = os.environ.copy()
            restart_env['PORT'] = '8080'
            restart_env.pop('PAYMENT_GATEWAY_URL', None)
            process = start_source(output, restart_env)
            http['GET /loans after restart'] = observe_http('GET', '/loans', None)
        finally:
            stop_gateway(gateway, gateway_thread)
            stop_source(process)
    write_or_compare('http', http, args.record)
    write_or_compare('browser', browser, args.record)
    write_or_compare('gateway', gateway_observations, args.record)
    action = 'recorded' if args.record else 'verified'
    print(f'{action} {len(http)} HTTP cases and {len(browser["pages"])} browser pages')


if __name__ == '__main__':
    main()
