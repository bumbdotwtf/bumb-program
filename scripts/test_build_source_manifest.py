"""Regression checks for compiler inputs omitted by earlier build records."""
import tempfile
import unittest
from pathlib import Path
from build_source_manifest import source_manifest


class BuildInputsTests(unittest.TestCase):
    def test_workspace_lock_and_ancestor_idl_mutations_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crate = root / 'programs/fees'
            inputs = ('Cargo.toml', 'Cargo.lock', 'idls/pump.json',
                      'programs/fees/Cargo.toml', 'programs/fees/src/lib.rs',
                      'programs/fees/idls/pump_amm.json', '.cargo/config.toml')
            for name in (*inputs, 'programs/fees/target/generated.rs', 'programs/fees/README.md'):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('original')
            before = source_manifest(crate, root, root)
            self.assertEqual(set(before), set(inputs))
            for name in ('Cargo.lock', 'idls/pump.json', 'programs/fees/idls/pump_amm.json'):
                p = root / name
                p.write_text('changed')
                self.assertNotEqual(before[name], source_manifest(crate, root, root)[name])
                p.unlink()
                self.assertNotIn(name, source_manifest(crate, root, root))

    def test_explicit_assets_must_exist_and_are_hash_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / 'tables.bin'
            asset.write_bytes(b'one')
            before = source_manifest(root, root, root, [asset])
            asset.write_bytes(b'two')
            self.assertNotEqual(before['tables.bin'], source_manifest(root, root, root, [asset])['tables.bin'])
            asset.unlink()
            with self.assertRaises(FileNotFoundError):
                source_manifest(root, root, root, [asset])


if __name__ == '__main__':
    unittest.main()
