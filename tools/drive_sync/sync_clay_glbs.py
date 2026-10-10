"""Save the clay building candidates to a Google Drive folder.

Uploads every `tools/clay_*/candidates/*.glb` (and, with --evidence, each family's latest
evidence folder as a zip) into one Drive folder, creating a sub-folder per family. Uploads are
idempotent: a file is replaced only when its sha256 differs from the `sha256` property stored
on the Drive file, so repeated runs on an unchanged branch do nothing.

Credentials (either works; OAuth is the right choice for a personal My Drive, a service
account for a Workspace Shared Drive):

  GDRIVE_OAUTH_CLIENT_ID, GDRIVE_OAUTH_CLIENT_SECRET, GDRIVE_OAUTH_REFRESH_TOKEN
      obtained once with `python tools/drive_sync/sync_clay_glbs.py authorize`
  GDRIVE_SERVICE_ACCOUNT_JSON
      the JSON key of a service account that has edit access to the folder

Target folder: GDRIVE_FOLDER_ID or --folder-id (the folder id from the Drive URL).

Examples:
  python tools/drive_sync/sync_clay_glbs.py plan                      # dry run, no network
  python tools/drive_sync/sync_clay_glbs.py sync --folder-id <id>     # upload
  python tools/drive_sync/sync_clay_glbs.py sync --evidence           # plus evidence zips
"""
import argparse
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
FOLDER_MIME = 'application/vnd.google-apps.folder'
API = 'https://www.googleapis.com/drive/v3'
UPLOAD = 'https://www.googleapis.com/upload/drive/v3'
SCOPE = 'https://www.googleapis.com/auth/drive.file'
DEFAULT_FOLDER_ID = '1CEqRJ4pZ5IuR-C6LQM0x_XKmTfA9Cx2U'   # snapshots/CityPrompt-clay-buildings-2026-10-10


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def families():
    out = []
    for fam in sorted(ROOT.glob('tools/clay_*')):
        glbs = sorted((fam / 'candidates').glob('*.glb')) if (fam / 'candidates').is_dir() else []
        if glbs:
            out.append((fam, glbs))
    return out


def latest_evidence_zip(fam, workdir):
    versions = sorted(p for p in (fam / 'evidence').glob('v*') if p.is_dir()) if (fam / 'evidence').is_dir() else []
    if not versions:
        return None
    v = versions[-1]
    out = workdir / f'{fam.name}-evidence-{v.name}.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(v.rglob('*')):
            if p.is_file():
                z.write(p, str(p.relative_to(v)))
        for extra in ('README.md', 'VERSIONS.md', 'sources.json'):
            if (fam / extra).is_file():
                z.write(fam / extra, extra)
    return out


def plan(args):
    workdir = Path(args.workdir); workdir.mkdir(parents=True, exist_ok=True)
    items = []
    for fam, glbs in families():
        for g in glbs:
            items.append(dict(family=fam.name, name=g.name, path=str(g.relative_to(ROOT)), bytes=g.stat().st_size, sha256=sha256(g), mime='model/gltf-binary'))
        if args.evidence:
            z = latest_evidence_zip(fam, workdir)
            if z:
                items.append(dict(family=fam.name, name=z.name, path=str(z), bytes=z.stat().st_size, sha256=sha256(z), mime='application/zip'))
    return items


# ---------------------------------------------------------------- credentials
def oauth_token():
    cid, secret, refresh = (os.environ.get(k) for k in ('GDRIVE_OAUTH_CLIENT_ID', 'GDRIVE_OAUTH_CLIENT_SECRET', 'GDRIVE_OAUTH_REFRESH_TOKEN'))
    if not (cid and secret and refresh):
        return None
    r = requests.post('https://oauth2.googleapis.com/token', data=dict(client_id=cid, client_secret=secret, refresh_token=refresh, grant_type='refresh_token'), timeout=30)
    r.raise_for_status()
    return r.json()['access_token']


def service_account_token():
    raw = os.environ.get('GDRIVE_SERVICE_ACCOUNT_JSON')
    if not raw:
        return None
    from google.oauth2 import service_account          # google-auth, already in backend/requirements.txt
    from google.auth.transport.requests import Request
    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(info, scopes=[SCOPE])
    creds.refresh(Request())
    return creds.token


def token():
    t = oauth_token() or service_account_token()
    if not t:
        sys.exit('No Drive credentials: set GDRIVE_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN (run `authorize` once) or GDRIVE_SERVICE_ACCOUNT_JSON.')
    return t


def authorize(args):
    """One-time local consent flow that prints the refresh token to store as a secret."""
    cid = os.environ.get('GDRIVE_OAUTH_CLIENT_ID') or input('OAuth client id: ').strip()
    secret = os.environ.get('GDRIVE_OAUTH_CLIENT_SECRET') or input('OAuth client secret: ').strip()
    import http.server, urllib.parse, webbrowser
    port = 8765
    redirect = f'http://localhost:{port}/'
    url = ('https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(dict(
        client_id=cid, redirect_uri=redirect, response_type='code', scope=SCOPE, access_type='offline', prompt='consent')))
    code = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            code['value'] = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('code', [''])[0]
            self.send_response(200); self.end_headers(); self.wfile.write(b'Authorised. You can close this tab.')

        def log_message(self, *a):
            pass

    print('Opening the Google consent page; sign in with the account that owns the Drive folder.\n' + url)
    webbrowser.open(url)
    http.server.HTTPServer(('localhost', port), H).handle_request()
    r = requests.post('https://oauth2.googleapis.com/token', data=dict(code=code['value'], client_id=cid, client_secret=secret, redirect_uri=redirect, grant_type='authorization_code'), timeout=30)
    r.raise_for_status()
    print('\nStore these as repository secrets:\n  GDRIVE_OAUTH_CLIENT_ID=' + cid + '\n  GDRIVE_OAUTH_CLIENT_SECRET=' + secret + '\n  GDRIVE_OAUTH_REFRESH_TOKEN=' + r.json()['refresh_token'])


# ---------------------------------------------------------------- drive calls
class Drive:
    def __init__(self, tok):
        self.s = requests.Session(); self.s.headers['Authorization'] = 'Bearer ' + tok

    def call(self, method, url, **kw):
        for attempt in range(5):
            r = self.s.request(method, url, timeout=120, **kw)
            if r.status_code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(2 ** attempt); continue
            if r.status_code >= 400:
                sys.exit(f'Drive API {r.status_code}: {r.text[:400]}')
            return r.json() if r.text else {}

    def find(self, name, parent):
        q = f"name = '{name}' and '{parent}' in parents and trashed = false"
        return self.call('GET', f'{API}/files', params=dict(q=q, fields='files(id,name,appProperties)', supportsAllDrives='true', includeItemsFromAllDrives='true')).get('files', [])

    def folder(self, name, parent):
        found = self.find(name, parent)
        if found:
            return found[0]['id']
        return self.call('POST', f'{API}/files', params=dict(supportsAllDrives='true'), json=dict(name=name, mimeType=FOLDER_MIME, parents=[parent]))['id']

    def upload(self, path, name, parent, mime, digest, existing=None):
        meta = dict(name=name, appProperties=dict(sha256=digest))
        if existing is None:
            meta['parents'] = [parent]
            url, method = f'{UPLOAD}/files?uploadType=multipart&supportsAllDrives=true', 'POST'
        else:
            url, method = f'{UPLOAD}/files/{existing}?uploadType=multipart&supportsAllDrives=true', 'PATCH'
        with open(path, 'rb') as f:
            files = {'metadata': ('metadata', json.dumps(meta), 'application/json; charset=UTF-8'), 'file': (name, f, mime)}
            return self.call(method, url, files=files)


def sync(args):
    items = plan(args)
    folder_id = args.folder_id or os.environ.get('GDRIVE_FOLDER_ID') or DEFAULT_FOLDER_ID
    d = Drive(token())
    uploaded, unchanged = [], []
    for it in items:
        sub = d.folder(it['family'], folder_id)
        found = d.find(it['name'], sub)
        if found and (found[0].get('appProperties') or {}).get('sha256') == it['sha256']:
            unchanged.append(it['name']); continue
        d.upload(it['path'] if Path(it['path']).is_absolute() else ROOT / it['path'], it['name'], sub, it['mime'], it['sha256'], found[0]['id'] if found else None)
        uploaded.append(it['name'])
    index = '\n'.join(f"| {it['family']} | {it['name']} | {it['bytes']:,} | {it['sha256'][:16]} |" for it in items)
    text = ('# Clay building candidates synced from CityPrompt\n\nBranch: ' + os.environ.get('GITHUB_REF_NAME', 'local') + '  \nCommit: ' + os.environ.get('GITHUB_SHA', 'local')[:12] +
            '  \nSynced: ' + time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()) + '\n\n| family | file | bytes | sha256 prefix |\n|---|---|---|---|\n' + index + '\n')
    idx = Path(args.workdir) / 'SYNC-INDEX.md'; idx.write_text(text)
    found = d.find('SYNC-INDEX.md', folder_id)
    d.upload(idx, 'SYNC-INDEX.md', folder_id, 'text/markdown', sha256(idx), found[0]['id'] if found else None)
    print(json.dumps(dict(folder=folder_id, uploaded=uploaded, unchanged=unchanged), indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['plan', 'sync', 'authorize'])
    p.add_argument('--folder-id', default=None)
    p.add_argument('--evidence', action='store_true', help='also upload a zip of each family\'s latest evidence folder')
    p.add_argument('--workdir', default=str(ROOT / '.drive-sync'))
    a = p.parse_args()
    if a.command == 'plan':
        print(json.dumps(plan(a), indent=2))
    elif a.command == 'authorize':
        authorize(a)
    else:
        sync(a)


if __name__ == '__main__':
    main()
