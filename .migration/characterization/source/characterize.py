import argparse
import difflib
import json
import os
import re
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
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
    ('unknown-loan', 'GET /loans/{id}', 'GET', '/loans/unknown', None),
    ('unknown-fee', 'GET /fees/{id}', 'GET', '/fees/unknown', None),
    ('unknown-payment', 'POST /payments/{id}', 'POST', '/payments/unknown', None),
    ('missing-loan-fields', 'POST /loans', 'POST', '/loans', {}),
    ('missing-loan-isbn', 'POST /loans', 'POST', '/loans', {'member': 'dee'}),
    ('empty-loan-fields', 'POST /loans', 'POST', '/loans', {'member': '', 'isbn': ''}),
    ('semicolon-member', 'POST /loans', 'POST', '/loans', {'member': 'a;b', 'isbn': '456'}),
    ('new-loan-zero-fee', 'GET /fees/{id}', 'GET', '/fees/L4', None),
    ('unknown-return', 'POST /loans/{id}/return', 'POST', '/loans/unknown/return', None),
    ('repeat-return', 'POST /loans/{id}/return', 'POST', '/loans/L1/return', None),
    ('loans-after-mutations', 'GET /loans', 'GET', '/loans', None),
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


def exercise_cases(cases):
    observations = {}
    for name, endpoint, method, path, form in cases:
        observations[name] = {
            'endpoint': endpoint,
            'request': {
                'method': method,
                'path': path,
                'form': form,
            },
            'response': get_response(method, path, form),
        }
    return observations


def stop_source(process):
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@contextmanager
def running_source():
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            ['bash', str(RUN_SCRIPT)],
            cwd=SOURCE,
            env=os.environ.copy(),
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            wait_until_ready(process, output)
            yield
        finally:
            stop_source(process)


def exercise_restart():
    return {
        'seed-loans-after-restart': {
            'endpoint': 'GET /loans',
            'request': {'method': 'GET', 'path': '/loans', 'form': None},
            'response': get_response('GET', '/loans', None),
        },
        'returned-loan-after-restart': {
            'endpoint': 'GET /loans/{id}',
            'request': {'method': 'GET', 'path': '/loans/L1', 'form': None},
            'response': get_response('GET', '/loans/L1', None),
        },
    }


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


def normalize_cases(observations):
    return {
        name: {
            'endpoint': observation['endpoint'],
            **normalize(observation, observation['endpoint']),
        }
        for name, observation in observations.items()
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
    elif name in {'edges', 'restart'}:
        actual = normalize_cases(observation)
        baseline = normalize_cases(expected)
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
    with running_source():
        http = exercise_http()
        edges = exercise_cases(EDGE_CASES)
        browser = exercise_browser()
    with running_source():
        restart = exercise_restart()
    write_or_compare('http', http, args.record)
    write_or_compare('edges', edges, args.record)
    write_or_compare('restart', restart, args.record)
    write_or_compare('browser', browser, args.record)
    action = 'recorded' if args.record else 'verified'
    case_count = len(http) + len(edges) + len(restart) + len(browser['pages'])
    print(
        f'{action} {len(http)} source endpoints, {len(edges)} edge cases, '
        f'{len(restart)} restart cases, and {len(browser["pages"])} browser pages '
        f'({case_count} observations)'
    )


if __name__ == '__main__':
    main()
