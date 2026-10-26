"""Run installed adapter fixtures and explicit Cargo entry-path escape regressions."""
from pathlib import Path
import importlib.util,sys,unittest
R=Path(__file__).resolve().parents[1]
P=R/'repro/build-tooling/supported-sbpf-proposal'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
fixtures=load('supported_proposal_fixtures',P/'test_proposal.py')
fixtures.adapter=load('installed_supported_adapter',R/'scripts/build_supported_sbpf_candidate.py')
fixtures.wrapper=load('installed_supported_wrapper',R/'scripts/build_reconstruction_candidate.py')
class InstalledPolicyTests(fixtures.ProposalTests):
 def target_case(self,body):
  (self.crate/'Cargo.toml').write_text(self.toml+body)
  with self.assertRaisesRegex(ValueError,'Cargo target/build'):
   self.plan('--dry-run')
  self.assertFalse(self.output.exists())
 def test_absolute_lib_path_rejected(self):
  (self.crate/'Cargo.toml').write_text(self.toml.replace('name="fixture_lib"','name="fixture_lib"\npath="/tmp/unrecorded.rs"'))
  with self.assertRaisesRegex(ValueError,'absolute Cargo target/build'):self.plan('--dry-run')
 def test_absolute_build_path_rejected(self):
  (self.crate/'Cargo.toml').write_text(self.toml.replace('name="fixture"','name="fixture"\nbuild="/tmp/unrecorded.rs"'))
  with self.assertRaisesRegex(ValueError,'absolute Cargo target/build'):self.plan('--dry-run')
 def test_absolute_bin_path_rejected(self):
  self.target_case('\n[[bin]]\nname="unrecorded"\npath="/tmp/unrecorded.rs"\n')
 def test_relative_unrecorded_lib_path_rejected(self):
  (self.crate/'Cargo.toml').write_text(self.toml.replace('name="fixture_lib"','name="fixture_lib"\npath="../unrecorded.rs"'))
  with self.assertRaisesRegex(ValueError,'outside the recorded snapshot'):self.plan('--dry-run')
if __name__=='__main__':unittest.main()
