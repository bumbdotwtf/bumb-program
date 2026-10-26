"""Git-location receipt binding, exact comparison and portable offline replay."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import analyze
import verify_vcs


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        findings = analyze.analyze()
        cls.queries = verify_vcs.expected_queries(analyze.PACKAGE, findings)
        cls.observations = json.loads(gzip.decompress(
            (analyze.PACKAGE / 'vcs-observations.json.gz').read_bytes()))['observations']

    def test_missing_or_duplicate_query_cannot_reduce_scope(self):
        for rows in (self.observations[:-1], self.observations + self.observations[:1]):
            with self.subTest(length=len(rows)), self.assertRaisesRegex(ValueError, 'inventory'):
                verify_vcs.compare_observations(self.queries, rows)

    def test_wrong_repository_commit_path_and_member_hash_rejected(self):
        for key in ('declared_repository', 'commit', 'path', 'url', 'archive_member_sha256'):
            rows = copy.deepcopy(self.observations)
            rows[0][key] = 'substituted'
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'binding differs'):
                verify_vcs.compare_observations(self.queries, rows)

    def test_partial_or_changed_source_is_not_an_exact_match(self):
        for contents in (self.observations[0]['result'][:-1], self.observations[0]['result'] + '\n'):
            rows = copy.deepcopy(self.observations)
            rows[0]['result'] = contents
            compared = verify_vcs.compare_observations(self.queries, rows)
            self.assertEqual(compared[0]['outcome'], 'different_member')

    def test_network_failure_cannot_be_misclassified_as_missing_commit(self):
        rows = copy.deepcopy(self.observations)
        rows[-1]['result']['error_data']['status'] = '503'
        with self.assertRaisesRegex(ValueError, 'Unexpected unresolved'):
            verify_vcs.compare_observations(self.queries, rows)


class RelocatedReplayTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.repo = self.root / 'repository'
        self.package = self.repo / 'research/metaplex-published-source'
        shutil.copytree(analyze.PACKAGE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        for relative in analyze.EXTERNAL:
            destination = self.repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(analyze.REPO / relative, destination)

    def run_verifier(self, *extra):
        return subprocess.run([sys.executable, '-B', str(self.package / 'verify_vcs.py'), *extra],
                              cwd=self.root, text=True, capture_output=True)

    def test_minimal_relocated_replay(self):
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary['queried_program_versions'], 49)
        self.assertEqual(summary['exact_member_matches'], 44)
        self.assertEqual(len(summary['unresolved_declared_commits']), 5)
        self.assertEqual(len(summary['program_versions_without_vcs_metadata']), 7)
        self.assertEqual(summary['different_members'], [])

    def test_changed_receipt_rejected_even_if_findings_are_rewritten(self):
        path = self.package / 'vcs-observations.json.gz'
        observed = json.loads(gzip.decompress(path.read_bytes()))
        observed['observations'][0]['result'] += '\n'
        path.write_bytes(gzip.compress(json.dumps(observed).encode(), mtime=0))
        (self.package / 'vcs-findings.json').write_text('{}')
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('observation seal differs', result.stderr)

    def test_recompression_of_identical_receipts_is_accepted(self):
        path = self.package / 'vcs-observations.json.gz'
        path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=1))
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_saved_findings_rejected(self):
        path = self.package / 'vcs-findings.json'
        report = json.loads(path.read_bytes())
        report['summary']['exact_member_matches'] = 49
        path.write_text(json.dumps(report))
        result = self.run_verifier()
        self.assertEqual(result.returncode, 2)
        self.assertIn('Saved Git findings differ', result.stderr)

    def test_existing_output_is_preserved_before_input_reads(self):
        path = self.root / 'existing.json'
        path.write_bytes(b'preserved')
        result = self.run_verifier('--package', str(self.root / 'missing'), '--output', str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn('Output already exists', result.stderr)
        self.assertEqual(path.read_bytes(), b'preserved')


if __name__ == '__main__':
    unittest.main()
