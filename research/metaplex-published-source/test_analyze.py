"""Regression and relocated-replay checks for the saved registry evidence."""
import gzip
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

from analyze import EXTERNAL, PACKAGE, REPO, block_present, members, utilize_observation


def tar_bytes(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as archive:
        for name, data, kind in entries:
            item = tarfile.TarInfo(name)
            item.type = kind
            item.size = len(data)
            archive.addfile(item, io.BytesIO(data))
    return stream.getvalue()


class SourceObservationTests(unittest.TestCase):
    def test_hunk_requires_consecutive_complete_normalized_lines(self):
        self.assertTrue(block_present('a();\n  b( x );\nc();', 'b(x);\nc();'))
        self.assertFalse(block_present('a();\nextra();\nb();', 'a();\nb();'))
        self.assertFalse(block_present('prefix_a();', 'a();'))
        self.assertFalse(block_present('a();', ''))

    def test_legacy_observation_is_scoped_to_the_utilize_function(self):
        raw = (b'pub fn before() { number_of_uses == 0; }\n'
               b'pub fn process_utilize() {\n'
               b'let metadata_uses = metadata.uses.unwrap();\n'
               b'if number_of_uses > metadata_uses.total || number_of_uses > metadata_uses.remaining {\n'
               b'}\n}\n'
               b'pub fn after() { number_of_uses == 0; }\n')
        result = utilize_observation('src/processor.rs', raw)
        self.assertFalse(result['literal_zero_equality_in_function'])
        self.assertTrue(result['contains_exact_two_disjunct_guard'])
        self.assertEqual(result['metadata_unwrap_lines'], [3])
        self.assertEqual(result['function_end_line_exclusive'], 7)

    def test_archive_rejects_ambiguous_or_nonregular_members(self):
        for entries in [
            [('same', b'a', tarfile.REGTYPE), ('same', b'b', tarfile.REGTYPE)],
            [('../escape', b'a', tarfile.REGTYPE)],
            [('/absolute', b'a', tarfile.REGTYPE)],
            [('link', b'', tarfile.SYMTYPE)],
        ]:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                members(tar_bytes(entries))

    def test_literal_zero_guard_detection_handles_both_operand_orders(self):
        for condition in ('number_of_uses == 0', '0 == number_of_uses'):
            raw = f'pub fn process_utilize() {{\nif {condition} {{}}\n}}'.encode()
            self.assertTrue(utilize_observation('utilize.rs', raw)['literal_zero_equality_in_function'])


class RelocatedReplayTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name) / 'copied-repository'
        self.package = self.repo / 'research' / 'metaplex-published-source'
        shutil.copytree(PACKAGE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        for relative in EXTERNAL:
            destination = self.repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, destination)

    def run_verifier(self, *extra):
        return subprocess.run([sys.executable, '-B', str(self.package / 'analyze.py'), *extra],
                              cwd=self.directory.name, text=True, capture_output=True)

    def test_minimal_relocated_repository_recomputes_all_findings(self):
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary['archives'], 57)
        self.assertEqual(summary['program_handler_versions'], 56)
        self.assertEqual(summary['pairs_not_in_prior_git_history_packet'], 108)
        self.assertEqual(summary['literal_zero_guard_versions'], 0)

    def test_changed_archive_fails_before_tar_parsing(self):
        path = next((self.package / 'archives').glob('*.crate'))
        path.write_bytes(b'changed archive')
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('SHA-256 mismatch', result.stderr)

    def test_changed_registry_snapshot_is_not_trusted(self):
        path = self.package / 'crate-metadata.json'
        path.write_bytes(path.read_bytes() + b' ')
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('SHA-256 mismatch', result.stderr)

    def test_changed_acquisition_receipt_is_rejected(self):
        path = self.package / 'download-receipts.json'
        path.write_bytes(path.read_bytes() + b' ')
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('SHA-256 mismatch', result.stderr)

    def test_missing_archive_cannot_silently_reduce_scope(self):
        path = next((self.package / 'archives').glob('*.crate'))
        path.rename(self.repo / 'omitted.crate')
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('Archive inventory differs', result.stderr)

    def test_changed_saved_finding_is_rejected(self):
        path = self.package / 'findings.json.gz'
        saved = json.loads(gzip.decompress(path.read_bytes()))
        saved['summary']['literal_zero_guard_versions'] = 1
        path.write_bytes(gzip.compress(json.dumps(saved).encode(), mtime=0))
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('Saved findings differ', result.stderr)

    def test_changed_external_source_evidence_is_rejected(self):
        path = self.repo / next(iter(EXTERNAL))
        path.write_bytes(path.read_bytes() + b' ')
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('SHA-256 mismatch', result.stderr)

    def test_existing_output_is_preserved_before_input_reads(self):
        path = self.repo / 'existing.json'
        path.write_bytes(b'preserved evidence')
        result = self.run_verifier('--package', str(self.repo / 'missing'), '--output', str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn('Output already exists', result.stderr)
        self.assertEqual(path.read_bytes(), b'preserved evidence')


if __name__ == '__main__':
    unittest.main()
