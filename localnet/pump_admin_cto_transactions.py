#!/usr/bin/env python3
"""Normally signed offline Pump admin CTO Surfpool comparisons with genuine dependency CPIs."""
import argparse,base64,hashlib,json,re,socket,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import pump_admin_cto_differential as f
import pump_distribution_transactions as engine
from solders.pubkey import Pubkey
PORT=20091
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f.TOKEN22=Pubkey.from_string('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb')
class RecordingVM(engine.RecordingVM):
 def with_transaction_history(self,n):self.vm=self.vm.with_transaction_history(n);return self

def prepare(case):
 original=f.LiteSVM;recorded=[]
 def factory():
  vm=RecordingVM(original());recorded.append(vm);return vm
 f.LiteSVM=factory
 try:receipt=f.run(case)
 finally:f.LiteSVM=original
 vm=recorded[0]
 return {'case':case,'accounts':vm.accounts,'transaction_base64':base64.b64encode(bytes(vm.transaction)).decode(),'litesvm_error':receipt['error']}

def event_layouts():
 out={}
 for name in ['pump','pump_amm','pump_fees']:
  idl=json.loads((ROOT/f'evidence/upstream/{name}.json').read_text());types={t['name']:t for t in idl['types']}
  for event in idl['events']:
   fields=types[event['name']]['type']['fields'];offset=8
   for field in fields:
    if field['name']=='timestamp':
     assert field['type']=='i64';out[bytes(event['discriminator']).hex()]=(offset,event['name']);break
    typ=field['type']
    if not isinstance(typ,str) or typ not in {'pubkey','u64','i64','bool','u8','u16','u32'}:break
    offset+={'pubkey':32,'u64':8,'i64':8,'bool':1,'u8':1,'u16':2,'u32':4}[typ]
 return out

def events(row,layouts):
 out=[]
 for log in row['logs']:
  if log.startswith('Program data: '):
   data=bytearray(base64.b64decode(log.split(': ',1)[1]));key=data[:8].hex();assert key in layouts,('Unknown event layout',key)
   offset,name=layouts[key];data[offset:offset+8]=bytes(8);out.append({'event':name,'data_except_timestamp':data.hex()})
 return out

def expected_error(value):
 if value is None:return None
 m=re.fullmatch(r'TransactionErrorInstructionError\(\((\d+), Tagged\(InstructionErrorCustom\((\d+)\)\)\)\)',value)
 if m:return {'InstructionError':[int(m[1]),{'Custom':int(m[2])}]}
 m=re.fullmatch(r'TransactionErrorInstructionError\(\((\d+), Fieldless\((\w+)\)\)\)',value)
 if m:return {'InstructionError':[int(m[1]),m[2]]}
 raise AssertionError(value)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--surfpool',type=Path,default=ROOT/'work/localnet/surfpool');a=p.parse_args();a.output=a.output.resolve();a.surfpool=a.surfpool.resolve()
 assert subprocess.check_output([str(a.surfpool),'--version'],text=True).strip()=='surfpool 1.6.1'
 for port in [PORT,PORT+1]:
  with socket.socket() as s:s.bind(('127.0.0.1',port))
 a.output.mkdir(parents=True,exist_ok=False);original=a.output/'original.so';candidate=a.output/'candidate.so';original.write_bytes((ROOT/'evidence/original/pump/deployed.so').read_bytes());candidate.write_bytes(a.candidate.read_bytes())
 wanted=['base','holder-none','holder-sweep-1000000','wallet-True-1000000','wallet-False-0','no-new','holder-new','wrong-authority','stable-2','stable-7','stable-8','token22-1','token22-2','holder-amm-transfer-False-1000000','holder-amm-transfer-True-1000000','amm-funds-False-1000000','token-dest-True-2','token-dest-False-2','curve-bool-48','curve-state-81-1','holder-disabled-1','fee-boundary-301','resize-rent-81-1','wrong-pump_fees_event_authority']
 cases=[c for c in f.cases() if c['name'] in wanted];assert len(cases)==len(wanted)
 paths=[Path(__file__),Path(f.__file__),Path(engine.__file__)]+[ROOT/f'evidence/upstream/{n}.json' for n in ['pump','pump_fees','pump_amm']]+[ROOT/f'evidence/original/{n}/deployed.so' for n in ['pump_fees','pump_amm']]+[ROOT/f'evidence/dependencies/{n}/deployed.so' for n in ['spl_token','spl_token_2022','associated_token']]
 hashes={str(path.relative_to(ROOT)):sha(path) for path in paths};fixtures=[prepare(c) for c in cases];(a.output/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
 oldf,oldport=engine.f,engine.PORT;engine.f,engine.PORT=f,PORT
 try:x=engine.run(original,fixtures,a.surfpool,a.output);y=engine.run(candidate,fixtures,a.surfpool,a.output)
 finally:engine.f,engine.PORT=oldf,oldport
 layouts=event_layouts();bad=[];unexpected=[]
 for fixture,l,r in zip(fixtures,x,y):
  if l['error']!=expected_error(fixture['litesvm_error']):unexpected.append(l['case']['name'])
  if any(l[k]!=r[k] for k in ['error','before','after']) or events(l,layouts)!=events(r,layouts):bad.append(l['case']['name'])
 assert all(sha(ROOT/path)==h for path,h in hashes.items());assert sha(candidate)==sha(a.candidate)
 report={'scope':'Normal verified signed offline Pump admin_cto transactions with captured Fees/AMM/Token/Token22/ATA CPI dependencies and synthetic fixtures. Exact account/error comparisons and schema-normalized event timestamps; raw logs retained. Return data retained, not compared here. Full byte identity remains false.','original_sha256':sha(original),'candidate_sha256':sha(candidate),'runner_sha256':sha(Path(__file__)),'fixture_script_sha256':sha(Path(f.__file__)),'surfpool_sha256':sha(a.surfpool),'provenance':hashes,'cases':len(cases),'signed_transactions':len(x)+len(y),'mismatches':bad,'unexpected_original_errors':unexpected,'original':x,'candidate':y}
 (a.output/'pump-admin-cto-transactions.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['cases','signed_transactions','mismatches','unexpected_original_errors','candidate_sha256']},indent=2))
 if bad or unexpected:raise SystemExit(1)
if __name__=='__main__':main()
