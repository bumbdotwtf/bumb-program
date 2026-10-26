"""Raw-byte gate regression tests; no compiler, VM or network required."""
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from byte_diff import PREVIEW_BYTES, report

SCRIPT = Path(__file__).with_name('byte_diff.py')


class ByteDiffTests(unittest.TestCase):
    def test_disjoint_changes_and_tail_have_exact_offsets(self):
        result = report(b'abcdef\0\0', b'axcXYf')
        self.assertEqual([(r['start'], r['end'], r['kind']) for r in result['ranges']],
                         [(1, 2, 'changed'), (3, 5, 'changed'), (6, 8, 'candidate_missing')])
        self.assertEqual(result['different_positions_in_shared_length'], 3)
        self.assertEqual(result['differing_or_missing_original_positions'], 5)
        self.assertEqual(result['ranges'][-1]['original_hex_prefix'], '0000')
        self.assertEqual(result['ranges'][-1]['candidate_hex_prefix'], '')

    def test_zero_allocation_tail_is_never_accepted_implicitly(self):
        result = report(b'ELF\0\0', b'ELF')
        self.assertFalse(result['full_byte_equality'])
        self.assertEqual(result['first_difference'], 3)
        self.assertEqual(result['missing_candidate_bytes'], 2)
        self.assertEqual(result['candidate_sha256'], hashlib.sha256(b'ELF').hexdigest())

    def test_extra_bytes_are_distinct_from_missing_original_positions(self):
        result = report(b'ab', b'ax\0')
        self.assertEqual(result['differing_or_missing_original_positions'], 1)
        self.assertEqual(result['total_differing_positions'], 2)
        self.assertEqual(result['extra_candidate_bytes'], 1)
        self.assertEqual(result['ranges'][-1]['kind'], 'candidate_extra')

    def test_range_cap_preserves_complete_totals(self):
        for limit in (0, 1, 2):
            with self.subTest(limit=limit):
                result = report(b'abcdef\0', b'xbcxef', limit)
                self.assertEqual(result['range_count'], 3)
                self.assertEqual(len(result['ranges']), limit)
                self.assertEqual(result['ranges_omitted'], 3 - limit)
                self.assertEqual(result['total_differing_positions'], 3)
                self.assertFalse(result['full_byte_equality'])

    def test_preview_is_bounded_without_shortening_the_range(self):
        result = report(b'a' * 1000, b'b' * 1000)
        row = result['ranges'][0]
        self.assertEqual(row['length'], 1000)
        self.assertEqual(row['original_hex_prefix'], (b'a' * PREVIEW_BYTES).hex())
        self.assertEqual(row['candidate_hex_prefix'], (b'b' * PREVIEW_BYTES).hex())

    def test_all_short_binary_pairs_against_positional_oracle(self):
        values = [bytes(bits) for size in range(4)
                  for bits in itertools.product((0, 1), repeat=size)]
        for original, candidate in itertools.product(values, repeat=2):
            with self.subTest(original=original, candidate=candidate):
                result = report(original, candidate)
                expected = {
                    offset for offset in range(max(len(original), len(candidate)))
                    if original[offset:offset + 1] != candidate[offset:offset + 1]
                }
                observed = [offset for row in result['ranges']
                            for offset in range(row['start'], row['end'])]
                self.assertEqual(set(observed), expected)
                self.assertEqual(len(observed), len(expected))
                self.assertEqual(result['total_differing_positions'], len(expected))
                self.assertEqual(result['full_byte_equality'], original == candidate)
                self.assertEqual(result['first_difference'], min(expected, default=None))
                self.assertFalse(result['source_provenance_verified'])

    def test_negative_limit_rejected(self):
        with self.assertRaises(ValueError):
            report(b'', b'', -1)


class ByteDiffCliTests(unittest.TestCase):
    def run_diff(self, *args):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True)

    def test_cli_exit_status_and_input_preservation(self):
        for candidate, expected_exit in [(b'abc\0\0', 0), (b'abc', 1), (b'axc\0\0', 1)]:
            with self.subTest(candidate=candidate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                original_path, candidate_path = root / 'original.so', root / 'candidate.so'
                original_path.write_bytes(b'abc\0\0')
                candidate_path.write_bytes(candidate)
                output = root / 'reports' / 'diff.json'
                completed = self.run_diff(original_path, candidate_path, '--output', output)
                self.assertEqual(completed.returncode, expected_exit, completed.stderr)
                result = json.loads(output.read_text(encoding='utf-8'))
                self.assertEqual(json.loads(completed.stdout), result)
                self.assertEqual(result['full_byte_equality'], expected_exit == 0)
                self.assertEqual(original_path.read_bytes(), b'abc\0\0')
                self.assertEqual(candidate_path.read_bytes(), candidate)

    def test_existing_report_and_input_output_paths_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original, candidate, output = root / 'a', root / 'b', root / 'report.json'
            original.write_bytes(b'a')
            candidate.write_bytes(b'b')
            output.write_bytes(b'previous evidence')
            for destination in (output, original, candidate):
                before = destination.read_bytes()
                completed = self.run_diff(original, candidate, '--output', destination)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(destination.read_bytes(), before)

    def test_invalid_arguments_do_not_write_a_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'source', root / 'report.json'
            source.write_bytes(b'abc')
            for original, extra in [(source, ['--max-ranges', '-1']), (root / 'missing', [])]:
                completed = self.run_diff(original, source, '--output', output, *extra)
                self.assertEqual(completed.returncode, 2)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
