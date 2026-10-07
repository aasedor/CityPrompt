"""Prepare exact hosted assets from Git/locked seeds, never local experiments.

No generation, catalogue approval or deployment. Output must be a new external
directory. --fetch-lfs downloads only the finite requested tracked paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LFS = b"version https://git-lfs.github.com/spec/v1"


def stamp_service_worker(source: str, identity: bytes) -> str:
    """A new release must not reuse cached non-fingerprinted model/image URLs."""
    name = "cityprompt-release-" + hashlib.sha256(identity).hexdigest()[:20]
    result, count = re.subn(r"^const CACHE_NAME = '[^']+';", f"const CACHE_NAME = '{name}';", source, count=1)
    if count != 1:
        raise ValueError("Cannot identify service worker cache; review release invalidation")
    return result


def safe_target(root: Path, url: str) -> Path:
    if not url.startswith("/") or url.startswith("//") or any(c in url for c in "\\:?#%"):
        raise ValueError("Expected an unescaped site-relative asset URL")
    relative = PurePosixPath(url[1:])
    if not relative.parts or ".." in relative.parts:
        raise ValueError("Unsafe public asset path")
    target = (root / str(relative)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("Asset escaped output directory")
    return target


def checked_payload(data: bytes, expected: str | None) -> bytes:
    if not data or data.startswith(LFS) or data.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise ValueError("Missing binary payload or unhydrated Git LFS pointer")
    if expected and hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Asset does not match its exact SHA-256 revision")
    return data


def write_asset(root: Path, url: str, data: bytes) -> dict:
    target = safe_target(root, url)
    if target.exists() and target.read_bytes() != data:
        raise ValueError(f"Preserved conflicting output: {url}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(data)
    return {"url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def public_requirements(report: dict) -> dict[str, dict]:
    checks = [check for choice in report["choices"] for check in choice["checks"]]
    for key in ("saved_layout_dependencies", "saved_model_revisions", "rustic_park_dependencies"):
        checks.extend(report.get(key, []))
    result = {}
    for check in checks:
        url = check.get("url")
        if not url:
            continue
        safe_target(Path("public"), url)
        previous = result.get(url, {})
        if previous.get("sha256") and check.get("sha256") and previous["sha256"] != check["sha256"]:
            raise ValueError(f"Conflicting revisions for {url}")
        result[url] = {**previous, **check}
    return result


def validate_packet(assets: Path, sources) -> dict:
    receipt = json.loads((assets / "assets.json").read_text())
    if receipt.get("schema") != "cityprompt.hosted-assets@1" or receipt.get("catalogue_activation") is not False:
        raise ValueError("Expected a verified hosted-assets packet")
    inputs = receipt.get("source_inputs")
    if not inputs or sources.fingerprint(inputs) != inputs:
        raise ValueError("Asset packet is stale; prepare it from the current source")
    metadata = {p for p in sources.tracked if p.startswith("frontend/src/")} | (sources.metadata_paths & sources.tracked)
    if not metadata <= inputs.keys():
        raise ValueError("Asset packet predates current catalogue source files")
    expected_files = {safe_target(assets / "public", asset["url"]) for asset in receipt["assets"]}
    actual_files = {p.resolve() for p in (assets / "public").rglob("*") if p.is_file()}
    if actual_files != expected_files:
        raise ValueError("Asset packet contains missing or unlisted public files")
    for asset in receipt["assets"]:
        data = checked_payload(safe_target(assets / "public", asset["url"]).read_bytes(), asset["sha256"])
        if len(data) != asset["bytes"]:
            raise ValueError("Hosted asset size changed")
    return receipt


def browser_environment(source: dict, env_dir: Path, public: Path) -> dict:
    origin = source.get("VITE_API_URL", "").rstrip("/")
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.path or parsed.query or parsed.fragment
            or parsed.hostname in {"localhost", "127.0.0.1", "::1"}):
        raise ValueError("VITE_API_URL must be the hosted HTTPS API origin, without /api or credentials")
    if not source.get("VITE_GOOGLE_MAPS_API_KEY", "").strip():
        raise ValueError("Set a restricted browser Maps key before building")
    # Preserve process essentials, not server/provider keys or a developer dotenv.
    essentials = {"path", "systemroot", "windir", "temp", "tmp", "home", "userprofile", "comspec", "pathext", "ci"}
    env = {key: value for key, value in source.items() if key.lower() in essentials}
    for key in ("VITE_GOOGLE_MAPS_API_KEY", "VITE_MAPBOX_TOKEN", "VITE_SENTRY_DSN"):
        if source.get(key):
            env[key] = source[key]
    env.update(VITE_API_URL=origin, VITE_WS_URL=origin.replace("https://", "wss://", 1),
               VITE_ENV_DIR=str(env_dir.resolve()), CITYPROMPT_PUBLIC_DIR=str(public.resolve()), NODE_ENV="production")
    return env


class RepositoryAssets:
    metadata_paths = {"seed/validation/manifest.json", "seed/validation/supplemental-2026-10-07/manifest.json"}
    def __init__(self, repo: Path, fetch_lfs: bool = False):
        self.repo, self.fetch_lfs = repo.resolve(), fetch_lfs
        self.tracked = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=repo, text=True).split("\0"))
        common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=repo, text=True).strip()
        self.lfs = (repo / common).resolve() / "lfs/objects"
        self.pointer = re.compile(rb"^version https://git-lfs.github.com/spec/v1\r?\noid sha256:([a-f0-9]{64})\r?\nsize (\d+)\r?\n?$")
        self.archive = None
        self.seed = json.loads(self.read("seed/validation/manifest.json"))
        self.members = {row["path"]: row for row in self.seed["files"]}
        self.by_hash = {row["sha256"]: row["path"] for row in self.seed["files"]}
        self.supplement = {row["url"]: row for row in json.loads(self.read("seed/validation/supplemental-2026-10-07/manifest.json"))["assets"]}
        self.park_sources = {}
        parks = json.loads(self.read("frontend/src/data/nativeParks.json"))
        for park in [*parks["layouts"], *parks.get("archivedLayouts", [])]:
            for asset in [*park["assets"].values(), *([park["thumbnail"]] if park.get("thumbnail") else [])]:
                self.park_sources[asset["url"]] = asset

    def lfs_object(self, digest: str, size: int | None = None) -> bytes:
        path = self.lfs / digest[:2] / digest[2:4] / digest
        data = checked_payload(path.read_bytes(), digest)
        if size is not None and len(data) != size:
            raise ValueError("Git LFS object size differs")
        return data

    def fingerprint(self, paths) -> dict[str, str]:
        result = {}
        for relative in sorted(paths):
            path = (self.repo / relative).resolve()
            if relative not in self.tracked or not path.is_relative_to(self.repo):
                raise ValueError("Asset receipt references an untracked source")
            data = path.read_bytes()
            pointer = self.pointer.fullmatch(data)
            if pointer:
                result[relative] = pointer[1].decode()
            else:
                if path.suffix.lower() in {".json", ".ts", ".tsx", ".js", ".mjs", ".css", ".html", ".svg"}:
                    data = data.replace(b"\r\n", b"\n")
                result[relative] = hashlib.sha256(data).hexdigest()
        return result

    def prefetch(self, paths: set[str]) -> None:
        """Batch exact missing paths instead of making thousands of LFS calls."""
        if not self.fetch_lfs:
            return
        missing = []
        for relative in sorted(paths):
            if relative not in self.tracked:
                raise ValueError(f"Untracked LFS input: {relative}")
            path = (self.repo / relative).resolve()
            if not path.is_relative_to(self.repo):
                raise ValueError("Runtime source escaped repository")
            if path.stat().st_size > 512:
                continue
            match = self.pointer.fullmatch(path.read_bytes())
            if match:
                digest = match[1].decode()
                if not (self.lfs / digest[:2] / digest[2:4] / digest).is_file():
                    missing.append(relative)
        batch = []
        for relative in missing:
            if batch and len(",".join([*batch, relative])) > 6000:
                subprocess.run(["git", "lfs", "fetch", "origin", "--include=" + ",".join(batch), "--exclude="], cwd=self.repo, check=True)
                batch = []
            batch.append(relative)
        if batch:
            subprocess.run(["git", "lfs", "fetch", "origin", "--include=" + ",".join(batch), "--exclude="], cwd=self.repo, check=True)

    def read(self, relative: str) -> bytes:
        if relative not in self.tracked or not relative.startswith(("frontend/public/", "frontend/src/data/", "seed/")):
            raise ValueError(f"Source is not a tracked runtime input: {relative}")
        path = (self.repo / relative).resolve()
        if not path.is_relative_to(self.repo):
            raise ValueError("Runtime source escaped repository")
        data = path.read_bytes()
        match = self.pointer.fullmatch(data)
        if match:
            digest, size = match[1].decode(), int(match[2])
            try:
                return self.lfs_object(digest, size)
            except FileNotFoundError:
                if not self.fetch_lfs:
                    raise ValueError(f"Hydrate Git LFS input: {relative}") from None
                subprocess.run(["git", "lfs", "fetch", "origin", f"--include={relative}", "--exclude="], cwd=self.repo, check=True)
                return self.lfs_object(digest, size)
        return checked_payload(data, None)

    def member(self, name: str) -> bytes:
        if name not in self.members:
            raise ValueError(f"Unpinned validation archive member: {name}")
        if self.archive is None:
            import io
            data = checked_payload(self.read("seed/validation/runtime-assets.zip"), self.seed["archive_sha256"])
            self.archive = zipfile.ZipFile(io.BytesIO(data))
        row = self.members[name]
        data = checked_payload(self.archive.read(name), row["sha256"])
        if len(data) != row["bytes"]:
            raise ValueError("Validation member size differs")
        return data

    def public(self, url: str, digest: str | None = None) -> bytes:
        relative = "frontend/public" + url
        if relative in self.tracked:
            return checked_payload(self.read(relative), digest)
        if url in self.supplement:
            row = self.supplement[url]
            return checked_payload(self.read(row["path"]), digest or row["sha256"])
        if url in self.park_sources:
            row = self.park_sources[url]
            data = self.read(row["archivePath"]) if row["archivePath"].startswith("seed/") else self.member(row["archivePath"])
            return checked_payload(data, digest or row["sha256"])
        member = "public" + url
        if member in self.members:
            return checked_payload(self.member(member), digest)
        if digest in self.by_hash:
            return self.member(self.by_hash[digest])
        if digest and url.startswith("/model-revisions/"):
            return self.lfs_object(digest)
        raise ValueError(f"No portable, pinned source for {url}")


def prepare(output: Path, fetch_lfs: bool = False) -> dict:
    output = output.resolve()
    if output.exists() or output.is_relative_to(ROOT) or ROOT.is_relative_to(output):
        raise ValueError("Choose a new output directory outside the repository")
    output.mkdir(parents=True)
    sources = RepositoryAssets(ROOT, fetch_lfs)
    env = dict(os.environ)
    for key in ("CITYPROMPT_PUBLIC_DIR", "CITYPROMPT_CATALOGUE_PACKET", "VITE_ENV_DIR"):
        env.pop(key, None)
    report_path = output / "catalogue-metadata.json"
    subprocess.run(["node", "frontend/scripts/check-catalogue-delivery.mjs", "--metadata-only", f"--report={report_path}"], cwd=ROOT, env=env, check=True)
    report = json.loads(report_path.read_text())
    private = [check for choice in report["choices"] for check in choice["checks"] if check.get("sourcePath")]
    required = public_requirements(report)
    # These small common domains include landing, people, map legends/tiles,
    # render examples, PWA files and the existing optional park surface skins.
    extra_prefixes = ("frontend/public/policy-maps/", "frontend/public/render-style-examples/",
                      "frontend/public/assets/", "frontend/public/entourage/", "frontend/public/images/", "frontend/public/park-skins/")
    for path in sorted(sources.tracked):
        if path.startswith(extra_prefixes) or (path.startswith("frontend/public/") and path.count("/") == 2):
            required.setdefault(path.removeprefix("frontend/public"), {})
    fetch_paths = {check["sourcePath"] for check in private}
    for url in required:
        tracked = "frontend/public" + url
        if tracked in sources.tracked:
            fetch_paths.add(tracked)
        elif url in sources.supplement:
            fetch_paths.add(sources.supplement[url]["path"])
        elif url in sources.park_sources and sources.park_sources[url]["archivePath"].startswith("seed/"):
            fetch_paths.add(sources.park_sources[url]["archivePath"])
        else:
            fetch_paths.add("seed/validation/runtime-assets.zip")
    sources.prefetch(fetch_paths)
    # Hydrate private audit sources without copying them into public storage.
    for check in private:
        checked_payload(sources.read(check["sourcePath"]), check.get("sha256"))
    public = output / "public"
    assets = [write_asset(public, url, sources.public(url, item.get("sha256"))) for url, item in sorted(required.items())]
    # Full audit also verifies backend Model Library sources, but doesn't seed or publish them.
    env["CITYPROMPT_PUBLIC_DIR"] = str(public)
    subprocess.run(["node", "frontend/scripts/check-catalogue-delivery.mjs", f"--report={output / 'catalogue-audit.json'}"], cwd=ROOT, env=env, check=True)
    receipt = {"schema": "cityprompt.hosted-assets@1", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "catalogue_activation": False, "choice_count": report["choice_count"], "assets": assets,
               "source_inputs": sources.fingerprint(fetch_paths | sources.metadata_paths | {p for p in sources.tracked if p.startswith("frontend/src/")}),
               "bytes": sum(row["bytes"] for row in assets)}
    (output / "assets.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fetch-lfs", action="store_true")
    args = parser.parse_args()
    result = prepare(args.output, args.fetch_lfs)
    print(json.dumps({"assets": len(result["assets"]), "bytes": result["bytes"], "choices": result["choice_count"]}))


if __name__ == "__main__":
    main()
