"""Check the research wrapper preserves experiments and frozen-helper integrity."""
import hashlib
from pathlib import Path
import unittest
from build_reconstruction_candidate import ROOT, command


class ResearchSelectionTests(unittest.TestCase):
    def test_default_does_not_select_header_incompatible_older_family(self):
        for name in ('pump', 'pump_amm', 'pump_fees'):
            argv=command(['--program',name,'--manifest','sample/Cargo.toml','--output','work/build'])
            self.assertEqual(argv[argv.index('--tools-version')+1], 'v1.44')
            self.assertIn('sample/Cargo.toml', argv)
        argv=command(['--program','mayhem'])
        self.assertEqual(argv[argv.index('--tools-version')+1], 'v1.52')

    def test_explicit_experiment_and_argument_boundaries_are_preserved(self):
        tail=['--program','pump','--tools-version=v1.43','--output','work/path with spaces']
        argv=command(tail)
        self.assertEqual(argv[2:],tail)
        self.assertNotIn('--tools-version',argv)

    def test_current_helper_matches_accepted_historical_helper(self):
        frozen=ROOT/'repro/pump_fees/sharing-pump-extend-main-v144/helpers/scripts/build_partial_candidate.py'
        self.assertEqual((ROOT/'scripts/build_partial_candidate.py').read_bytes(), frozen.read_bytes())


if __name__ == '__main__':
    unittest.main()
