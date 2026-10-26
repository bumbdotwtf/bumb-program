"""Fixture/argv tests only. No validator or transaction is executed."""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROPOSAL=Path(__file__).resolve().parents[1]/'repro/parallel-work/2026-10-25/independent-reconstruction-review/localnet-sdk-testing'
spec=importlib.util.spec_from_file_location('localnet_proposal', PROPOSAL/'start_localnet.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda b:hashlib.sha256(b).hexdigest()

class LocalnetProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='sdk-plan-')
        self.root=Path(self.temp.name).resolve();self.here=self.root/'harness';self.here.mkdir();(self.root/'work').mkdir()
        self.programs={n:'core-'+n for n in ['pump','pump_amm','pump_fees','mayhem']}
        self.status={}
        def save(p,d):
            p=self.root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d))
        self.save=save
        for n,a in self.programs.items():
            cp=f'builds/{n}.so';rp=f'builds/{n}.json';raw=('candidate-'+n).encode();target=('target-'+n).encode()
            (self.root/cp).parent.mkdir(exist_ok=True);(self.root/cp).write_bytes(raw)
            self.status[n]={'candidate_artifact':cp,'comparison_report':rp}
            save(rp,{'program':n,'comparison':{'candidate_sha256':sha(raw),'original_sha256':sha(target)}})
            save(f'evidence/original/{n}/capture.json',{'program':a,'payload_sha256':sha(target)})
            (self.root/f'evidence/original/{n}/deployed.so').write_bytes(target)
        for n in m.DEPENDENCIES:
            raw=n.encode();save(f'evidence/dependencies/{n}/capture.json',{'program':'dep-'+n,'payload_sha256':sha(raw)})
            (self.root/f'evidence/dependencies/{n}/deployed.so').write_bytes(raw)
        save('repro/status.json',self.status);save('repro/programs.json',self.programs)
        for n in m.SEEDS:
            save(f'harness/seed-accounts/{n}_global.json',{'pubkey':'seed-'+n,'account':{'lamports':100,'data':[base64.b64encode(b'fixture').decode(),'base64'],'owner':self.programs[n],'executable':False,'space':7}})
        self.ledger=self.root/'work/fresh'
    def tearDown(self):self.temp.cleanup()
    def plan(self):return m.prepare(self.root,self.here,self.ledger,8899)
    def test_all_nine_programs_relay_and_no_reset(self):
        p=self.plan();self.assertEqual(len(p['programs']),9);self.assertIn('donation_relay',[r['name'] for r in p['programs']]);self.assertNotIn('--reset',p['command']);self.assertFalse(self.ledger.exists());self.assertEqual(p['command'][p['command'].index('--bind-address')+1],'127.0.0.1')
    def test_missing_or_mutated_candidate_blocks(self):
        candidate=self.root/self.status['pump']['candidate_artifact'];candidate.write_bytes(b'wrong')
        with self.assertRaisesRegex(ValueError,'owning build'):self.plan()
        candidate.unlink()
        with self.assertRaises(FileNotFoundError):self.plan()
        self.assertFalse(self.ledger.exists())
    def test_existing_ledger_and_symlink_preserved(self):
        self.ledger.mkdir();marker=self.ledger/'keep';marker.write_text('keep')
        with self.assertRaisesRegex(ValueError,'fresh path'):self.plan()
        self.assertEqual(marker.read_text(),'keep');marker.unlink();self.ledger.rmdir()
        self.ledger.symlink_to(self.root/'nonexistent')
        with self.assertRaisesRegex(ValueError,'fresh path'):self.plan()
        self.assertTrue(self.ledger.is_symlink())
    def test_wrapper_and_mocked_validator_arguments(self):
        subprocess.run(['git','init','--quiet',str(self.root)],check=True)
        for name in ['start-localnet.sh','start_localnet.py']:shutil.copyfile(PROPOSAL/name,self.here/name)
        stub=self.root/'mock-bin';stub.mkdir();mock=stub/'solana-test-validator'
        mock.write_text('#!'+sys.executable+'\nimport json,sys; print("MOCK_VALIDATOR:"+json.dumps(sys.argv[1:]))\n');mock.chmod(0o755)
        env=os.environ.copy();env['PATH']=str(stub)+os.pathsep+env['PATH']
        result=subprocess.run(['bash',str(self.here/'start-localnet.sh'),str(self.ledger)],env=env,check=True,text=True,capture_output=True)
        line=next(l for l in result.stdout.splitlines()if l.startswith('MOCK_VALIDATOR:'));argv=json.loads(line.split(':',1)[1]);self.assertEqual(argv.count('--bpf-program'),9);self.assertIn('dep-donation_relay',argv);self.assertNotIn('--reset',argv);self.assertFalse(self.ledger.exists())
        result=subprocess.run(['bash',str(self.here/'start-localnet.sh'),'--dry-run',str(self.ledger)],env=env,check=True,text=True,capture_output=True);self.assertNotIn('MOCK_VALIDATOR:',result.stdout);self.assertEqual(len(json.loads(result.stdout)['programs']),9)
if __name__=='__main__':unittest.main()
