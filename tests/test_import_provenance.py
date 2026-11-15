"""Deterministic positive and hostile-input tests for historical import proof."""
import copy
import hashlib
import unittest

from scripts.verify_import_provenance import (
    ALLOWED_PATHS,
    IMPORT_COMMIT,
    SOURCE_REPOSITORY,
    verify_manifest,
    git_import_blob,
)


def demo():
    contents = {path: ("synthetic:" + path).encode() for path in sorted(ALLOWED_PATHS)}
    document = {
        "schema": "runner-preflight-clean-export-v1",
        "scope": "Public standalone source snapshot; no private project content or git history",
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": "a" * 40,
        "files": [
            {
                "path": path,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            for path, data in contents.items()
        ],
    }
    return document, contents


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.blobs = demo()

    def check(self, document=None, blobs=None):
        content = self.blobs if blobs is None else blobs
        return verify_manifest(
            self.manifest if document is None else document,
            lambda path: content[path],
        )

    def test_fixed_import_commit_and_success(self):
        self.assertEqual(len(IMPORT_COMMIT), 40)
        result = self.check()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["verified_files"], len(ALLOWED_PATHS))
        self.assertEqual(result["import_commit"], IMPORT_COMMIT)
        self.assertEqual(result["origin"], SOURCE_REPOSITORY)

    def test_modified_file_cannot_verify_original_import(self):
        modified = dict(self.blobs)
        modified["README.md"] += b"x"
        with self.assertRaisesRegex(ValueError, "SIZE_MISMATCH"):
            self.check(blobs=modified)
        modified["README.md"] = b"X" + self.blobs["README.md"][1:]
        with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
            self.check(blobs=modified)

    def test_extra_or_duplicate_file_rejected(self):
        for bad_path in ("../private/AGENTS.md", "README.md"):
            manifest = copy.deepcopy(self.manifest)
            manifest["files"][0]["path"] = bad_path
            with self.assertRaises(ValueError):
                self.check(document=manifest)

    def test_missing_file_and_unexpected_manifest_schema(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["files"].pop()
        with self.assertRaisesRegex(ValueError, "INCOMPLETE"):
            self.check(document=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["extra"] = {}
        with self.assertRaisesRegex(ValueError, "INVALID_MANIFEST_SCHEMA"):
            self.check(document=manifest)

    def test_no_unknown_source_or_checksum(self):
        for field, value in (
            ("source_repository", "private/control"),
            ("source_commit", "not-a-commit"),
            ("schema", "another-version"),
            ("scope", "includes private content"),
        ):
            manifest = copy.deepcopy(self.manifest)
            manifest[field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    self.check(document=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["files"][0]["sha256"] = "X" * 64
        with self.assertRaisesRegex(ValueError, "INVALID_FILE_HASH"):
            self.check(document=manifest)

    def test_bad_length_and_bool_size_fail(self):
        for bad_size in (-1, True, 200_000):
            manifest = copy.deepcopy(self.manifest)
            manifest["files"][0]["bytes"] = bad_size
            with self.subTest(size=bad_size):
                with self.assertRaisesRegex(ValueError, "INVALID_FILE_SIZE"):
                    self.check(document=manifest)

    def test_git_reader_rejects_untrusted_path_before_invoking_git(self):
        for unsafe in ("/etc/passwd", "../secrets", "rust/../../private"):
            with self.assertRaisesRegex(ValueError, "PATH_NOT_ALLOWED"):
                git_import_blob(None, unsafe)

    def test_missing_original_blob_fails_closed(self):
        deleted = dict(self.blobs)
        del deleted["README.md"]
        with self.assertRaises(KeyError):
            self.check(blobs=deleted)


if __name__ == "__main__":
    unittest.main()
