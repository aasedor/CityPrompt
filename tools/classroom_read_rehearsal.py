"""Finite, authenticated GET-only classroom API rehearsal. No provider calls.

The private fixture file binds tokens to one base URL. Provision disposable
local sessions with backend/scripts/prepare_classroom_rehearsal.py; a hosted
trial needs its own authorized sessions. This measures API reads, not WebGL,
login, saves, image queues, actual laptops or classroom-network performance.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from math import ceil
from pathlib import Path
from threading import Barrier
from time import perf_counter, sleep
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Unexpected redirect; verify the canonical API URL")


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, ceil(len(ordered) * fraction) - 1))]


def run(fixture, clients, rounds):
    base = fixture['base_url'].rstrip('/')
    parsed = urlparse(base)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.query or parsed.fragment:
        raise ValueError('Use a plain HTTP(S) base URL without embedded credentials')
    sessions = fixture['sessions'][:clients]
    if len(sessions) != clients or len({s['user_id'] for s in sessions}) != clients:
        raise ValueError('Each virtual client needs its own authenticated account')
    for session in sessions:
        uuid.UUID(session['project_id']); uuid.UUID(session['user_id'])
        if not isinstance(session['token'], str) or not session['token']:
            raise ValueError('Missing session token')
    barrier = Barrier(clients)

    def student(index):
        session = sessions[index]
        opener = build_opener(NoRedirect)
        samples = []
        checks = [
            ('projects', '/api/v1/projects/'),
            ('project', '/api/v1/projects/' + session['project_id']),
            ('zones', '/api/v1/site-zones/projects/' + session['project_id'] + '/zones'),
            ('references', '/api/v1/reference-layers/projects/' + session['project_id']),
        ]
        barrier.wait(timeout=30)
        for _ in range(rounds):
            for name, path in checks:
                start = perf_counter(); ok = False; status = 0; size = 0
                try:
                    request = Request(base + path, headers={'Authorization': 'Bearer ' + session['token'], 'Accept': 'application/json'})
                    with opener.open(request, timeout=20) as response:
                        status = response.status; body = response.read(8 * 1024 * 1024); size = len(body)
                        data = json.loads(body)
                        ok = status == 200
                        if name == 'project': ok = ok and data.get('id') == session['project_id']
                        if name == 'projects': ok = ok and any(row.get('id') == session['project_id'] for row in data)
                        if name == 'zones': ok = ok and len(data) >= fixture['minimum_zones'] and all(row.get('project_id') == session['project_id'] for row in data)
                except HTTPError as error: status = error.code
                except Exception: pass  # Record failure without printing credentials or response bodies.
                samples.append({'endpoint': name, 'ms': (perf_counter() - start) * 1000, 'ok': ok, 'status': status, 'bytes': size})
            sleep(.2)
        # Verify another simulated student's private project does not leak.
        other = sessions[(index + 1) % clients]
        if clients > 1:
            start = perf_counter(); status = 0
            try:
                with opener.open(Request(base + '/api/v1/projects/' + other['project_id'], headers={'Authorization': 'Bearer ' + session['token']}), timeout=20) as response:
                    status = response.status
            except HTTPError as error: status = error.code
            except Exception: pass
            samples.append({'endpoint': 'private_project_denial', 'ms': (perf_counter() - start) * 1000, 'ok': status in (403, 404), 'status': status, 'bytes': 0})
        return samples

    start = perf_counter()
    with ThreadPoolExecutor(max_workers=clients) as pool:
        samples = [sample for result in pool.map(student, range(clients)) for sample in result]
    duration = perf_counter() - start
    endpoints = {}
    for name in sorted({s['endpoint'] for s in samples}):
        rows = [s for s in samples if s['endpoint'] == name]; timings = [s['ms'] for s in rows]
        endpoints[name] = {'requests': len(rows), 'failures': sum(not s['ok'] for s in rows), 'p50_ms': round(percentile(timings, .5), 1),
                           'p95_ms': round(percentile(timings, .95), 1), 'max_ms': round(max(timings), 1), 'response_bytes': sum(s['bytes'] for s in rows)}
    return {'schema': 'cityprompt.classroom-read-rehearsal@1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
            'base_url': base, 'clients': clients, 'distinct_accounts': clients, 'distinct_projects': len({s['project_id'] for s in sessions}),
            'rounds': rounds, 'duration_seconds': round(duration, 2), 'requests': len(samples), 'failures': sum(not s['ok'] for s in samples),
            'scope': 'Pre-authenticated API reads and private-project denial; no login, writes, media generation or browser load simulation.', 'endpoints': endpoints}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--clients', type=int, default=40)
    parser.add_argument('--rounds', type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.clients <= 80 or not 1 <= args.rounds <= 20: parser.error('Bound the trial to 1–80 clients and 1–20 rounds')
    report = run(json.loads(args.fixtures.read_text(encoding='utf-8')), args.clients, args.rounds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 1 if report['failures'] else 0


if __name__ == '__main__': raise SystemExit(main())
