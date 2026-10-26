"""Corruption, attribution and isolated replay checks for actual hosted evidence."""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import verify_saved as verify


class SavedTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.package = Path(temporary.name) / 'isolated'
        self.package.mkdir()
        for name in ('observe.py', 'verify_saved.py', 'receipts.json.gz', '40332914951.zip', '40333550925.zip'):
            shutil.copyfile(verify.PACKAGE / name, self.package / name)

    def observed(self):
        with zipfile.ZipFile(self.package / '40333550925.zip') as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def replace_log(self, members, label, channel, raw):
        state = json.loads(members['observation.json'])
        row, = [row for row in state['commands'] if row['label'] == label]
        row[channel].update(bytes=len(raw), sha256=verify.sha(raw))
        members[row[channel]['file']] = raw
        members['observation.json'] = json.dumps(state).encode()

    def test_minimal_relocated_replay_without_repository_or_compiler(self):
        result = subprocess.run([sys.executable, '-B', str(self.package / 'verify_saved.py')],
                                cwd=self.package, capture_output=True, check=True)
        findings = json.loads(result.stdout)
        self.assertEqual(findings['artifact_members'], 95)
        self.assertEqual(len(findings['initialized_libraries']), 9)
        self.assertEqual(len(findings['capabilities']), 4)
        self.assertFalse(findings['historical_loaded_library_identity_proven'])
        self.assertEqual(findings['program_builds'], 0)

    def test_changed_zip_source_and_receipts_rejected(self):
        for name in ('40332914951.zip', '40333550925.zip', 'observe.py', 'receipts.json.gz'):
            path = self.package / name
            original = path.read_bytes()
            path.write_bytes(gzip.compress(gzip.decompress(original) + b' ', mtime=0)
                             if name.endswith('.gz') else original + b' ')
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'differs|Changed evidence'):
                verify.verify(self.package)
            path.write_bytes(original)

    def test_driver_swap_rejected_even_with_same_version_and_resealed_logs(self):
        members = self.observed()
        libraries = json.loads(members['loaded-libraries.json'])
        index, = [index for index, row in enumerate(libraries) if 'librustc_driver-' in row['resolved_path']]
        libraries[index]['sha256'] = '0' * 64
        members['loaded-libraries.json'] = json.dumps(libraries).encode()
        raw = ('0' * 64 + '  ' + libraries[index]['resolved_path'] + '\n').encode()
        self.replace_log(members, f'loaded-library-{index:02d}-sha256', 'stdout', raw)
        with self.assertRaisesRegex(ValueError, 'Loaded driver differs from archive'):
            verify.derive(members)

    def test_loader_search_attempt_does_not_prove_initialization(self):
        members = self.observed()
        raw = members['rustc-loaded-version.stderr.log'].replace(b'calling init:', b'trying file=')
        self.replace_log(members, 'rustc-loaded-version', 'stderr', raw)
        with self.assertRaisesRegex(ValueError, 'No loaded rustc driver'):
            verify.derive(members)

    def test_container_network_change_rejected(self):
        members = self.observed()
        state = json.loads(members['observation.json'])
        row, = [row for row in state['commands'] if row['label'] == 'start-container']
        row['command'][row['command'].index('--network') + 1] = 'host'
        members['observation.json'] = json.dumps(state).encode()
        with self.assertRaisesRegex(ValueError, 'Command differs: start-container'):
            verify.derive(members)

    def test_historical_attribution_cannot_be_promoted(self):
        members = self.observed()
        state = json.loads(members['observation.json'])
        state['historical_loaded_library_identity_proven'] = True
        members['observation.json'] = json.dumps(state).encode()
        with self.assertRaisesRegex(ValueError, 'Evidence scope was broadened'):
            verify.derive(members)

    def test_failed_capability_query_cannot_be_reported_as_success(self):
        members = self.observed()
        state = json.loads(members['observation.json'])
        row, = [row for row in state['commands'] if row['label'] == 'target-03-spec']
        row['returncode'] = 1
        members['observation.json'] = json.dumps(state).encode()
        with self.assertRaisesRegex(ValueError, 'Retained command failed'):
            verify.derive(members)


if __name__ == '__main__':
    unittest.main()
