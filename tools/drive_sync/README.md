# Saving the clay buildings to Google Drive

`sync_clay_glbs.py` copies every `tools/clay_*/candidates/*.glb` (and, with `--evidence`,
a zip of each family's latest `evidence/<version>/` folder plus its README, VERSIONS and
source lock) into one Google Drive folder, one sub-folder per family. It is idempotent:
a file is re-uploaded only when its sha256 changes, and `SYNC-INDEX.md` in the folder
records what was synced from which commit.

The target folder is `snapshots / CityPrompt-clay-buildings-2026-10-10`
(https://drive.google.com/drive/folders/1CEqRJ4pZ5IuR-C6LQM0x_XKmTfA9Cx2U). Override it
with `--folder-id` or the `GDRIVE_FOLDER_ID` variable.

The GitHub Action `.github/workflows/drive-sync.yml` runs the sync on every push that
changes a candidate or its evidence, and can be run by hand from the Actions tab. It does
nothing until the credentials below exist.

## One-time setup (about ten minutes, only you can do it)

The folder is in a personal My Drive, so the upload must run as your Google account
(a service account cannot own files in a personal My Drive). Steps:

1. Google Cloud console: create or pick a project, enable the **Google Drive API**.
2. **APIs and services > Credentials > Create credentials > OAuth client ID**, application
   type **Desktop app**. Note the client id and client secret. If the consent screen is in
   testing mode, add your own Google account as a test user.
3. On your machine, with the repository checked out:

   ```
   pip install requests
   GDRIVE_OAUTH_CLIENT_ID=<id> GDRIVE_OAUTH_CLIENT_SECRET=<secret> \
     python tools/drive_sync/sync_clay_glbs.py authorize
   ```

   A browser tab asks you to sign in and approve the `drive.file` scope (the script can
   only see files it creates). The script prints a refresh token.
4. GitHub repository **Settings > Secrets and variables > Actions**:
   - secrets `GDRIVE_OAUTH_CLIENT_ID`, `GDRIVE_OAUTH_CLIENT_SECRET`, `GDRIVE_OAUTH_REFRESH_TOKEN`
   - variable `GDRIVE_FOLDER_ID` = `1CEqRJ4pZ5IuR-C6LQM0x_XKmTfA9Cx2U` (or another folder)
5. Run the **Drive sync (clay buildings)** workflow once from the Actions tab, or push.

Workspace alternative: for a Shared Drive, create a service account, share the folder with
its email as Editor, and store its JSON key as the `GDRIVE_SERVICE_ACCOUNT_JSON` secret
instead of the three OAuth secrets.

## Phone-only setup (no local Python)

The refresh token can also be minted in a browser with Google's OAuth Playground:

1. In the Cloud console, create the OAuth client as type **Web application** (not Desktop) and add
   `https://developers.google.com/oauthplayground` under **Authorized redirect URIs**.
2. Open https://developers.google.com/oauthplayground, tap the gear icon, tick **Use your own OAuth
   credentials** and paste the client id and secret.
3. In Step 1 type the scope `https://www.googleapis.com/auth/drive.file`, tap **Authorize APIs**,
   sign in and allow. In Step 2 tap **Exchange authorization code for tokens** and copy the
   **Refresh token**.
4. Store the three secrets as above. Publish the consent screen to **In production** first, or the
   token expires after seven days.

With the `drive.file` scope the token cannot see a folder you made by hand in Drive. When the
target folder is not reachable the sync creates (and afterwards reuses) its own folder,
`CityPrompt clay buildings`, in My Drive, so `GDRIVE_FOLDER_ID` can be left unset.

## Running it locally

```
python tools/drive_sync/sync_clay_glbs.py plan              # lists what would be uploaded, no network
python tools/drive_sync/sync_clay_glbs.py sync --evidence   # uploads with the credentials in your environment
```

The `drive.file` scope means the token can only touch files this script created; it
cannot read or change anything else in the Drive.
