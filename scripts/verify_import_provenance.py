#!/usr/bin/env python3
"""Offline verification of the immutable public v0.2.0 source-import snapshot.

This checks files as recorded in the *original import commit* so that README,
workflow and contributor improvements can evolve without falsifying history.
It does NOT attest that the upstream source was trustworthy or grant runtime access.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Callable

IMPORT_COMMIT = "ea0c21d1a5da31fb59cafb31324f413256309739"
SOURCE_REPOSITORY = "esheenj/compound-intelligence-starter"
ALLOWED_PATHS = frozenset({
    ".github/workflows/ci.yml",
    "LICENSE",
    "README.md",
    "fixtures/hold-arch.json",
    "fixtures/job-linux-arm64.json",
    "fixtures/job-linux-x64.json",
    "fixtures/ready-x64.json",
    "fixtures/warn-disk.json",
    "rust/Cargo.lock",
    "rust/Cargo.toml",
    "rust/deny.toml",
    "rust/rust-toolchain.toml",
    "rust/src/main.rs",
    "scripts/collect_linux_runner.py",
    "tests/test_runner_preflight_collector.py",
})
SHA256_HEX = re.compile(r"[0-9a-f]{64}\Z")
SHA1_HEX = re.compile(r"[0-9a-f]{40}\Z")
SCHEMA = "runner-preflight-clean-export-v1"


def verify_manifest(document: object, read_snapshot: Callable[[str], bytes]) -> dict:
    """Validate all original allowlisted entries against original Git objects."""
    if not isinstance(document, dict) or set(document) != {
        "schema", "scope", "source_repository", "source_commit", "files"
    }:
        raise ValueError("INVALID_MANIFEST_SCHEMA")
    if document["schema"] != SCHEMA:
        raise ValueError("INVALID_MANIFEST_VERSION")
    if document["source_repository"] != SOURCE_REPOSITORY:
        raise ValueError("UNEXPECTED_SOURCE_REPOSITORY")
    if not isinstance(document["source_commit"], str) or not SHA1_HEX.fullmatch(document["source_commit"]):
        raise ValueError("INVALID_SOURCE_COMMIT")
    if document["scope"] != "Public standalone source snapshot; no private project content or git history":
        raise ValueError("UNEXPECTED_EXPORT_SCOPE")
    entries = document["files"]
    if not isinstance(entries, list) or len(entries) != len(ALLOWED_PATHS):
        raise ValueError("INCOMPLETE_FILE_MANIFEST")

    seen = set()
    total_bytes = 0
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "bytes"}:
            raise ValueError("INVALID_FILE_ENTRY")
        path, expected_hash, expected_size = entry["path"], entry["sha256"], entry["bytes"]
        if not isinstance(path, str) or path not in ALLOWED_PATHS or path in seen:
            raise ValueError("DUPLICATE_OR_UNEXPECTED_PATH")
        if not isinstance(expected_hash, str) or not SHA256_HEX.fullmatch(expected_hash):
            raise ValueError("INVALID_FILE_HASH")
        if type(expected_size) is not int or not 0 < expected_size <= 128_000:
            raise ValueError("INVALID_FILE_SIZE")
        # Only an exact reviewed path reaches the read-only git show callback.
        original_bytes = read_snapshot(path)
        if len(original_bytes) != expected_size:
            raise ValueError("ORIGINAL_FILE_SIZE_MISMATCH:" + path)
        if hashlib.sha256(original_bytes).hexdigest() != expected_hash:
            raise ValueError("ORIGINAL_FILE_HASH_MISMATCH:" + path)
        total_bytes += len(original_bytes)
        seen.add(path)
    if seen != ALLOWED_PATHS:
        raise ValueError("MISSING_ORIGINAL_FILES")
    return {"status": "PASS", "import_commit": IMPORT_COMMIT,
            "origin": SOURCE_REPOSITORY, "source_commit": document["source_commit"],
            "verified_files": len(seen), "verified_source_bytes": total_bytes,
            "scope": "immutable import-commit files only; not an upstream trust attestation"}


def git_import_blob(repository: Path, path: str) -> bytes:
    """Use local Git only; do not fetch network data or follow working-tree links."""
    if path not in ALLOWED_PATHS and path != "SOURCE_PROVENANCE.json":
        raise ValueError("PATH_NOT_ALLOWED")
    process = subprocess.run(
        ["git", "show", f"{IMPORT_COMMIT}:{path}"], cwd=repository,
        capture_output=True, timeout=10, check=True,
    )
    if len(process.stdout) > 128_000:
        raise ValueError("ORIGINAL_BLOB_TOO_LARGE")
    return process.stdout


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    recorded = (root / "SOURCE_PROVENANCE.json").read_bytes()
    if len(recorded) > 65_536:
        raise ValueError("MANIFEST_TOO_LARGE")
    if recorded != git_import_blob(root, "SOURCE_PROVENANCE.json"):
        raise ValueError("ORIGINAL_MANIFEST_WAS_MODIFIED")
    result = verify_manifest(
        json.loads(recorded.decode("utf-8")),
        lambda path: git_import_blob(root, path),
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
