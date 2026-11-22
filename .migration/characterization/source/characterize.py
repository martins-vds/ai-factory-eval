import argparse
import difflib
import json
import os
import re
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
    for endpoint, method, path, form in CASES:
        observations[endpoint] = {
            'request': {
                'method': method,
                'path': path,
                'form': form,
            },
            'response': get_response(method, path, form),
        }
    return observations


def observe(method, path, form=None):
    return {
        'request': {'method': method, 'path': path, 'form': form},
        'response': get_response(method, path, form),
    }


def exercise_edge_cases():
    cases = {
        'loan_missing_id': observe('GET', '/loans/missing'),
        'fee_missing_id': observe('GET', '/fees/missing'),
        'create_missing_both': observe('POST', '/loans'),
        'create_missing_member': observe('POST', '/loans', {'isbn': 'missing-member'}),
        'create_missing_isbn': observe('POST', '/loans', {'member': 'missing-isbn'}),
        'fee_l1_cap': observe('GET', '/fees/L1'),
        'fee_l2_zero': observe('GET', '/fees/L2'),
        'fee_l3_late': observe('GET', '/fees/L3'),
        'return_l2_before': observe('GET', '/loans/L2'),
        'return_l2_first': observe('POST', '/loans/L2/return'),
        'return_l2_again': observe('POST', '/loans/L2/return'),
        'return_missing_id': observe('POST', '/loans/missing/return'),
        'fee_l2_after_return': observe('GET', '/fees/L2'),
        'create_blank_fields': observe('POST', '/loans', {'member': '', 'isbn': ''}),
        'get_blank_fields': observe('GET', '/loans/L5'),
        'list_after_mutations': observe('GET', '/loans'),
    }
    if cases['loan_missing_id']['response']['status'] != 404:
        raise AssertionError('GET /loans/missing did not return 404')
    if cases['fee_missing_id']['response']['status'] != 404:
        raise AssertionError('GET /fees/missing did not return 404')
    if cases['create_missing_both']['response']['status'] != 500:
        raise AssertionError('bodyless POST /loans did not return the observed 500 response')
    if any(
        cases[name]['response']['status'] != 400
        for name in ('create_missing_member', 'create_missing_isbn')
    ):
        raise AssertionError('POST /loans did not return 400 for a partially missing form')
    if cases['create_blank_fields']['response']['status'] != 201:
        raise AssertionError('POST /loans did not accept present-but-empty form fields')
    if cases['return_missing_id']['response']['status'] != 404:
        raise AssertionError('POST /loans/missing/return did not return 404')
    if cases['return_l2_before']['response']['body'] != (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    ):
        raise AssertionError('seeded L2 return date differs from the characterized fixture')
    if cases['return_l2_first']['response']['status'] != 200:
        raise AssertionError('POST /loans/L2/return did not return 200')
    if cases['return_l2_first']['response']['body'] != cases['return_l2_again']['response']['body']:
        raise AssertionError('repeated return did not produce the same current-date record')
    if '2026-01-20' in cases['return_l2_first']['response']['body']:
        raise AssertionError('POST /loans/L2/return did not replace the prior return date')
    if any(
        cases[name]['response']['status'] != 200
        for name in ('fee_l1_cap', 'fee_l2_zero', 'fee_l3_late')
    ):
        raise AssertionError('a seeded loan fee request did not return 200')
    if 'Fee: $0.00' not in cases['fee_l2_zero']['response']['body']:
        raise AssertionError('the early-returned L2 fee was not zero')
    if 'Fee: $4.75' not in cases['fee_l3_late']['response']['body']:
        raise AssertionError('the 19-day-late L3 fee was not $4.75')
    if 'Fee: $10.00' not in cases['fee_l1_cap']['response']['body']:
        raise AssertionError('the overdue L1 fee was not capped at $10.00')
    if cases['get_blank_fields']['response']['status'] != 200:
        raise AssertionError('the blank-field loan was not persisted')
    if not cases['get_blank_fields']['response']['body'].startswith('L5;;;'):
        raise AssertionError('the blank-field loan did not retain empty member and ISBN fields')
    lines = cases['list_after_mutations']['response']['body'].splitlines()
    if len(lines) != 5 or lines != sorted(lines):
        raise AssertionError('the post-mutation loan list is not five records ordered by id')
    return cases


class GatewayHandler(BaseHTTPRequestHandler):
    status = 200
    body = b'approved\n'
    requests: ClassVar[list[dict[str, str]]] = []

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', '0'))
        self.__class__.requests.append(
            {
                'method': 'POST',
                'path': self.path,
                'body': self.rfile.read(content_length).decode('utf-8'),
            }
        )
        self.send_response(self.__class__.status)
        self.send_header('Content-Length', str(len(self.__class__.body)))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(self.__class__.body)
        self.close_connection = True

    def log_message(self, _format, *_args):
        pass


def start_application(output, gateway_url=None, package=False):
    env = os.environ.copy()
    env.pop('PAYMENT_GATEWAY_URL', None)
    env['PORT'] = '8080'
    command = (
        ['bash', str(RUN_SCRIPT)]
        if package
        else ['java', '-cp', 'target/classes:target/dependency/*', 'lib.App']
    )
    if gateway_url is not None:
        env['PAYMENT_GATEWAY_URL'] = gateway_url
    return subprocess.Popen(
        command,
        cwd=SOURCE,
        env=env,
        stdout=output,
        stderr=subprocess.STDOUT,
    )


def stop_application(process):
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def exercise_restart(created_loan_id):
    with tempfile.TemporaryFile() as output:
        process = start_application(output)
        try:
            wait_until_ready(process, output)
            observations = {
                'list_after_restart': observe('GET', '/loans'),
                'created_loan_after_restart': observe('GET', f'/loans/{created_loan_id}'),
            }
        finally:
            stop_application(process)
    if observations['created_loan_after_restart']['response']['status'] != 404:
        raise AssertionError(
            'a loan created before restart survived the in-memory database restart'
        )
    if observations['list_after_restart']['response']['body'].count('\n') != 3:
        raise AssertionError('restart did not restore exactly the three seeded loans')
    return observations


def exercise_gateway():
    GatewayHandler.requests = []
    server = ThreadingHTTPServer(('127.0.0.1', 0), GatewayHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    gateway_url = f'http://127.0.0.1:{server.server_address[1]}'
    with tempfile.TemporaryFile() as output:
        process = start_application(output, gateway_url=gateway_url)
        try:
            wait_until_ready(process, output)
            GatewayHandler.status = 200
            GatewayHandler.body = b'approved\n'
            success = observe('POST', '/payments/L3')
            GatewayHandler.status = 503
            GatewayHandler.body = b'gateway unavailable\n'
            gateway_error = observe('POST', '/payments/L3')
            requests_before_unknown = len(GatewayHandler.requests)
            unknown_loan = observe('POST', '/payments/missing')
            server.shutdown()
            server.server_close()
            thread.join(timeout=10)
            io_error = observe('POST', '/payments/L3')
        finally:
            stop_application(process)
            if thread.is_alive():
                server.shutdown()
                server.server_close()
                thread.join(timeout=10)
    observations = {
        'gateway_success': success,
        'gateway_non_200': gateway_error,
        'unknown_loan': unknown_loan,
        'gateway_io_error': io_error,
        'gateway_requests': GatewayHandler.requests,
    }
    if success['response']['status'] != 200 or success['response']['body'] != 'approved\n':
        raise AssertionError('a successful gateway response was not relayed')
    if (
        gateway_error['response']['status'] != 502
        or gateway_error['response']['body'] != 'gateway unavailable\n'
    ):
        raise AssertionError('a non-200 gateway response was not mapped to 502 with its body')
    if (
        unknown_loan['response']['status'] != 404
        or len(GatewayHandler.requests) != requests_before_unknown
    ):
        raise AssertionError('an unknown loan was not rejected before calling the gateway')
    if (
        io_error['response']['status'] != 502
        or io_error['response']['body'] != 'payment gateway unavailable\n'
    ):
        raise AssertionError('a gateway I/O failure did not produce the generic 502 response')
    if GatewayHandler.requests != [
        {'method': 'POST', 'path': '/charge?loan=L3', 'body': ''},
        {'method': 'POST', 'path': '/charge?loan=L3', 'body': ''},
    ]:
        raise AssertionError('gateway requests did not match the bodyless POST contract')
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
    if endpoint == 'GET /fees/{id}':
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


def normalize_responses(observation):
    if isinstance(observation, dict):
        normalized = {key: normalize_responses(value) for key, value in observation.items()}
        response = normalized.get('response')
        if response is not None:
            body = re.sub(r'\d{4}-\d{2}-\d{2}', '<date>', response['body'])
            body = re.sub(r'\d+ day\(s\) late', '<days> day(s) late', body)
            body = re.sub(r'Fee: \$\d+\.\d{2}', 'Fee: $<amount>', body)
            response['body'] = body
        return normalized
    if isinstance(observation, list):
        return [normalize_responses(value) for value in observation]
    return observation


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
    elif name in ('edges', 'lifecycle', 'gateway'):
        actual = normalize_responses(observation)
        baseline = normalize_responses(expected)
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
    with tempfile.TemporaryFile() as output:
        process = start_application(output, package=True)
        try:
            wait_until_ready(process, output)
            http = exercise_http()
            browser = exercise_browser()
            edges = exercise_edge_cases()
        finally:
            stop_application(process)
    created_loan_id = http['POST /loans']['response']['body'].split(';', 1)[0]
    lifecycle = exercise_restart(created_loan_id)
    gateway = exercise_gateway()
    write_or_compare('http', http, args.record)
    write_or_compare('browser', browser, args.record)
    write_or_compare('edges', edges, args.record)
    write_or_compare('lifecycle', lifecycle, args.record)
    write_or_compare('gateway', gateway, args.record)
    action = 'recorded' if args.record else 'verified'
    cases = len(http) + len(browser['pages']) + len(edges) + len(lifecycle) + 4
    print(
        f'{action} {cases} cases: {len(http)} source endpoints, {len(browser["pages"])} browser pages, '
        f'{len(edges)} edge cases, 2 lifecycle cases, 4 gateway cases'
    )


if __name__ == '__main__':
    main()
