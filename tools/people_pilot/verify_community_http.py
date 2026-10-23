"""Read-only exact-byte HTTP check for the twenty models and thumbnails."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path('C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/characters')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://127.0.0.1:5184')
    args = parser.parse_args()
    delivery = json.loads(Path(__file__).with_name('community_delivery.json').read_text())
    checked = []
    for expected in delivery['files']:
        with urllib.request.urlopen(args.base.rstrip('/') + expected['url'], timeout=20) as response:
            raw = response.read()
            digest = hashlib.sha256(raw).hexdigest()
            assert response.status == 200 and digest == expected['sha256'] and len(raw) == expected['bytes'], expected['url']
            checked.append({'url': expected['url'], 'sha256': digest, 'bytes': len(raw), 'contentType': response.headers.get('content-type')})
    assert len(checked) == 40
    (ROOT / 'http-delivery.json').write_text(json.dumps({'base': args.base, 'files': checked}, indent=2) + '\n')
    print('PASS 40/40 HTTP 200 exact-byte model/thumbnail responses at', args.base)
