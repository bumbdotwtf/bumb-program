"""Offline image evidence, narrow path-boundary and stream-corruption tests."""
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
from unittest.mock import patch

import fetch_layers
import verify


class BoundaryTests(unittest.TestCase):
    def test_cache_entry_or_root_alias_rejects_absence_conclusion(self):
        root = {'name': 'root', 'type': '5'}
        for row in ({'name': './root/.cache/solana/v1.37/rustc', 'type': '0'},
                    {'name': 'root/.cache', 'type': '2'}):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, 'cache entry'):
                verify.check_cache_boundary([[root], [row]])
        with self.assertRaisesRegex(ValueError, 'not a directory'):
            verify.check_cache_boundary([[{'name': 'root', 'type': '2'}]])

    def test_similar_name_does_not_create_false_cache_observation(self):
        roots = verify.check_cache_boundary([[{'name': 'root', 'type': '5'},
            {'name': 'root/.cache-other/example', 'type': '0'}]])
        self.assertEqual(len(roots), 1)

    def test_noncanonical_path_is_rejected(self):
        for name in ('../root', '/root'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Noncanonical'):
                verify.check_cache_boundary([[{'name': name, 'type': '5'}]])


class SavedTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.package = self.root / 'repository/research/metaplex-image-bootstrap'
        self.repo = self.package.parents[1]
        shutil.copytree(verify.PACKAGE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        for name in verify.HISTORICAL:
            relative = Path('repro/pump/metaplex-candidate-build-11') / name
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verify.REPO / relative, target)

    def test_minimal_relocated_replay(self):
        result = verify.verify(self.package, self.repo)
        self.assertEqual(result['headers_observed'], 28844)
        self.assertEqual(result['root_cache_entries'], 0)
        self.assertTrue(result['historical_tool_path_observed_after_build'])
        self.assertFalse(result['full_layer_replay'])
        self.assertFalse(result['historical_loaded_library_identity_proven'])

    def test_changed_manifest_config_source_and_receipts_rejected(self):
        for name in ('manifest.json', 'config.json', 'layers.json.gz', 'manifest-receipts.json.gz',
                     'upstream-receipts.json.gz', 'upstream/cargo-build-sbf-main.rs'):
            path = self.package / name
            original = path.read_bytes()
            path.write_bytes(gzip.compress(gzip.decompress(original) + b' ', mtime=0)
                             if name.endswith('.gz') else original + b' ')
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Changed evidence'):
                verify.verify(self.package, self.repo)
            path.write_bytes(original)

    def test_inventory_corruption_and_rewritten_seal_rejected(self):
        path = self.package / 'inventory-00.json.gz'
        raw = gzip.decompress(path.read_bytes()) + b' '
        path.write_bytes(gzip.compress(raw, mtime=0))
        with self.assertRaisesRegex(ValueError, 'inventory seal'):
            verify.verify(self.package, self.repo)
        path = self.package / 'layers.json.gz'
        rows = json.loads(gzip.decompress(path.read_bytes()))
        rows[0]['inventory_raw_sha256'] = verify.sha(raw)
        path.write_bytes(gzip.compress(json.dumps(rows).encode(), mtime=0))
        with self.assertRaisesRegex(ValueError, 'Changed evidence'):
            verify.verify(self.package, self.repo)

    def test_inventory_recompression_preserves_observation(self):
        path = self.package / 'inventory-00.json.gz'
        path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=1))
        self.assertEqual(verify.verify(self.package, self.repo)['root_cache_entries'], 0)

    def test_missing_layer_inventory_rejected(self):
        (self.package / 'inventory-07.json.gz').unlink()
        with self.assertRaises(FileNotFoundError):
            verify.verify(self.package, self.repo)

    def test_changed_historical_compiler_receipt_rejected(self):
        path = self.repo / 'repro/pump/metaplex-candidate-build-11/tool-versions.json'
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'Changed evidence'):
            verify.verify(self.package, self.repo)


class LayerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.blob = Path(directory.name) / 'fixture.tar.gz'
        stream = io.BytesIO()
        name, data = 'toolchain/sdk/sbf/scripts/install.sh', b'synthetic evidence, never executed\n'
        with tarfile.open(fileobj=stream, mode='w') as archive:
            info = tarfile.TarInfo(name)
            info.mode = 0o644
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
        self.raw = stream.getvalue()
        packed = gzip.compress(self.raw, mtime=0)
        self.blob.write_bytes(packed)
        row = {'name': name, 'type': '0', 'size': len(data), 'mode': 0o644, 'linkname': ''}
        self.saved = 'selected/' + verify.sha(data)
        self.expected = {'compressed_bytes': len(packed), 'blob_digest': 'sha256:' + verify.sha(packed),
            'uncompressed_bytes': len(self.raw), 'diff_id': 'sha256:' + verify.sha(self.raw),
            'inventory_raw_sha256': verify.sha(verify.inventory_bytes([row])),
            'selected': [dict(row, sha256=verify.sha(data), saved=self.saved)]}

    def test_complete_stream_including_tar_padding_is_checked(self):
        rows, retained = verify.measure_layer(self.blob, self.expected)
        self.assertEqual(len(rows), 1)
        self.assertEqual(retained[self.saved], b'synthetic evidence, never executed\n')

    def test_wrong_compressed_bytes_rejected_before_decompression(self):
        self.blob.write_bytes(b'not an archive')
        with self.assertRaisesRegex(ValueError, 'Compressed layer'):
            verify.measure_layer(self.blob, self.expected)

    def test_changed_trailing_tar_bytes_reject_even_with_updated_compressed_digest(self):
        changed = self.raw[:-1] + b'x'
        packed = gzip.compress(changed, mtime=0)
        self.blob.write_bytes(packed)
        self.expected.update(compressed_bytes=len(packed), blob_digest='sha256:' + verify.sha(packed))
        with self.assertRaisesRegex(ValueError, 'Uncompressed layer'):
            verify.measure_layer(self.blob, self.expected)


class DownloadTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.data = b'synthetic compressed bytes'
        self.descriptor = {'size': len(self.data), 'digest': 'sha256:' + verify.sha(self.data)}

    def response(self, raw):
        stream = io.BytesIO(raw)
        stream.status = 200
        return stream

    def test_verified_download_retains_exact_bytes(self):
        with patch('fetch_layers.urllib.request.urlopen', return_value=self.response(self.data)):
            result = fetch_layers.download(self.root, self.descriptor, {})
        self.assertTrue(result['verified'])
        self.assertEqual((self.root / result['saved']).read_bytes(), self.data)

    def test_failed_hash_retains_partial_evidence(self):
        with patch('fetch_layers.urllib.request.urlopen', return_value=self.response(b'wrong')):
            result = fetch_layers.download(self.root, self.descriptor, {})
        self.assertFalse(result['verified'])
        self.assertEqual((self.root / (result['saved'] + '.partial')).read_bytes(), b'wrong')
        self.assertFalse((self.root / result['saved']).exists())

    def test_existing_output_rejected_before_network(self):
        result = subprocess.run([sys.executable, '-B', str(verify.PACKAGE / 'fetch_layers.py'),
                                 '--output', str(self.root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Output already exists', result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
