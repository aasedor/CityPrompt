"""Provide Git LFS in Render's native build image when it is absent.

Only the build process PATH changes; no global installation or Git config edits.
Archive checksum: https://github.com/git-lfs/git-lfs/releases/tag/v3.7.1
"""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import tempfile
from urllib.request import urlopen

VERSION = "3.7.1"
URL = f"https://github.com/git-lfs/git-lfs/releases/download/v{VERSION}/git-lfs-linux-amd64-v{VERSION}.tar.gz"
SHA256 = "1c0b6ee5200ca708c5cebebb18fdeb0e1c98f1af5c1a9cba205a4c0ab5a5ec08"


def ensure_git_lfs() -> None:
    if subprocess.run(["git", "lfs", "version"], capture_output=True).returncode == 0:
        return
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise RuntimeError("Git LFS is required; install it before using --fetch-lfs on this platform")
    with urlopen(URL, timeout=60) as response:
        payload = response.read(32 * 1024 * 1024)
    if hashlib.sha256(payload).hexdigest() != SHA256:
        raise ValueError("Git LFS download checksum mismatch; refusing to execute it")
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        member = archive.getmember(f"git-lfs-{VERSION}/git-lfs")
        if not member.isfile() or member.size > 64 * 1024 * 1024:
            raise ValueError("Unexpected Git LFS executable in verified archive")
        binary = archive.extractfile(member)
        if binary is None:
            raise ValueError("Git LFS executable missing from verified archive")
        # Write only this known regular file, never extract archive paths/links.
        directory = Path(tempfile.mkdtemp(prefix="cityprompt-build-lfs-"))
        target = directory / "git-lfs"
        target.write_bytes(binary.read())
    target.chmod(0o755)
    os.environ["PATH"] = str(directory) + os.pathsep + os.environ.get("PATH", "")
    subprocess.run(["git", "lfs", "version"], check=True)
