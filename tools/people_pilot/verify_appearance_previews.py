"""Read-only HTTP/hash checks for local picker images and unchanged people assets."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

REPO = Path(__file__).resolve().parents[2]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://127.0.0.1:5184')
    args = parser.parse_args()
    root = REPO / 'frontend/src/features/people'
    actors = json.loads((root / 'peopleCatalogue.json').read_text(encoding='utf-8'))
    actors += json.loads((root / 'inclusivePeopleCatalogue.json').read_text(encoding='utf-8'))
    previews = json.loads((root / 'peopleAppearancePreviews.json').read_text(encoding='utf-8'))
    assert len(previews) == len(actors) and len(actors) >= 23
    assert len({a["id"] for a in actors}) == len(actors)
    assert {p['id'] for p in previews} == {a['id'] for a in actors}
    assert len({p['url'] for p in previews}) == len(actors)
    total = 0
    for preview in previews:
        with urlopen(args.base.rstrip('/') + preview['url'], timeout=20) as response:
            content = response.read()
            assert response.status == 200 and response.headers.get_content_type() == 'image/webp'
        assert content[:4] == b'RIFF' and content[8:12] == b'WEBP', preview['id']
        assert hashlib.sha256(content).hexdigest() == preview['sha256'], preview['id']
        assert len(content) == preview['bytes'] <= 100000
        total += len(content)
    for actor in actors:
        for url, expected in [(actor['url'], actor['sha256']),
                              (actor['thumbnailUrl'], actor['thumbnailSha256'])]:
            with urlopen(args.base.rstrip('/') + url, timeout=20) as response:
                content = response.read()
                assert response.status == 200
            assert hashlib.sha256(content).hexdigest() == expected, actor['id']
    print(f'PASS {len(actors)}/{len(actors)} WebP previews ({total:,} bytes), exact catalogue GLBs and source thumbnails')
