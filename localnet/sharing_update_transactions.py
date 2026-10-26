#!/usr/bin/env python3
"""Signed offline Surfpool sharing-update comparisons with captured CPI programs."""
import argparse,base64,hashlib,json,socket,struct,subprocess,sys,time,urllib.request
from pathlib import Path
from solders.hash import Hash
from solders.instruction import AccountMeta,Instruction
from solders.transaction import Transaction
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import fees_sharing_update_differential as f
PORT=20021
sha=lambda data:hashlib.sha256(data).hexdigest()
class RecordingVM:
 def __init__(self,vm):self.vm=vm;self.keys=set();self.accounts={};self.transaction=None
 def __getattr__(self,name):return getattr(self.vm,name)
 def set_account(self,key,account):self.keys.add(key);return self.vm.set_account(key,account)
 def send_transaction(self,tx):
  self.transaction=tx;self.accounts={}
  for key in self.keys:
   a=self.vm.get_account(key)
   if a and not a.executable:self.accounts[str(key)]={'lamports':a.lamports,'data':a.data.hex(),'owner':str(a.owner),'executable':False}
  return self.vm.send_transaction(tx)
def prepare(c):
 original=f.f.LiteSVM;recorded=[]
 def factory():
  vm=RecordingVM(original());recorded.append(vm);return vm
 f.f.LiteSVM=factory
 try:receipt=f.run(c)
 finally:f.f.LiteSVM=original
 vm=recorded[0]
 return {'case':c,'accounts':vm.accounts,'transaction_base64':base64.b64encode(bytes(vm.transaction)).decode(),'litesvm_error':receipt['error']}
def run(binary,cases,surfpool,output):
 def rpc(method,params=None):
  req=urllib.request.Request(f'http://127.0.0.1:{PORT}',data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=60) as response:result=json.load(response)
  if 'error' in result:raise RuntimeError((method,result['error']))
  return result['result']
 def get(key):
  a=rpc('getAccountInfo',[key,{'encoding':'base64'}])['value']
  return None if a is None else {'lamports':a['lamports'],'owner':a['owner'],'data':base64.b64decode(a['data'][0]).hex()}
 with (output/(binary.stem+'.log')).open('w') as log:
  proc=subprocess.Popen([str(surfpool),'start','--offline','--no-deploy','--no-tui','--no-studio','--host','127.0.0.1','--port',str(PORT),'--ws-port',str(PORT+1),'--airdrop-amount','0','--db',':memory:'],cwd=output,stdout=log,stderr=subprocess.STDOUT)
  try:
   for _ in range(100):
    if proc.poll() is not None:raise RuntimeError('Surfpool terminated')
    try:
     if rpc('getHealth')=='ok':break
    except OSError:pass
    time.sleep(.1)
   else:raise TimeoutError('Surfpool startup')
   programs=[(f.PROGRAM,binary),(f.PUMP,ROOT/'evidence/original/pump/deployed.so'),(f.AMM,ROOT/'evidence/original/pump_amm/deployed.so')]+[(key,ROOT/f'evidence/dependencies/{name}/deployed.so') for name,key in [('spl_token',f.TOKEN),('spl_token_2022',f.TOKEN22),('associated_token',f.ATA)]]
   for key,path in programs:
    blob=path.read_bytes();extent=struct.unpack_from('<Q',blob,40)[0]+struct.unpack_from('<H',blob,58)[0]*struct.unpack_from('<H',blob,60)[0];assert not any(blob[extent:])
    rpc('surfnet_setAccount',[str(key),{'lamports':10**10,'data':blob[:extent].hex(),'owner':'BPFLoader2111111111111111111111111111111111','executable':True}])
   rows=[];previous=set()
   for row in cases:
    for key in previous-set(row['accounts']):rpc('surfnet_setAccount',[key,{'lamports':0,'data':'','owner':str(f.Pubkey.default()),'executable':False}])
    for key,account in row['accounts'].items():rpc('surfnet_setAccount',[key,account])
    previous=set(row['accounts']);before={key:get(key) for key in row['accounts']}
    old=Transaction.from_bytes(base64.b64decode(row['transaction_base64']));msg=old.message;h=msg.header;keys=msg.account_keys
    def writable(i):return i<h.num_required_signatures-h.num_readonly_signed_accounts if i<h.num_required_signatures else i<len(keys)-h.num_readonly_unsigned_accounts
    instructions=[Instruction(keys[ix.program_id_index],bytes(ix.data),[AccountMeta(keys[n],n<h.num_required_signatures,writable(n)) for n in ix.accounts]) for ix in msg.instructions]
    # Distinct compute budgets avoid transaction deduplication for repeated payloads.
    instructions[0]=f.set_compute_unit_limit(1400000-len(rows))
    signers=[kp for kp in [f.PAYER,f.AUTH,f.OTHER] if kp.pubkey() in keys[:h.num_required_signatures]]
    tx=Transaction.new_signed_with_payer(instructions,f.PAYER.pubkey(),signers,Hash.from_string(rpc('getLatestBlockhash')['value']['blockhash']));assert all(tx.verify_with_results());encoded=base64.b64encode(bytes(tx)).decode()
    sim=rpc('simulateTransaction',[encoded,{'encoding':'base64','sigVerify':True}])['value'];sig=rpc('sendTransaction',[encoded,{'encoding':'base64','skipPreflight':True}])
    for _ in range(100):
     status=rpc('getSignatureStatuses',[[sig]])['value'][0]
     if status is not None:break
     time.sleep(.05)
    else:raise TimeoutError('Confirmation')
    assert status['err']==sim['err'];after={key:get(key) for key in row['accounts']}
    if status['err']:assert all(before[k]==after[k] for k in before if k!=str(f.PAYER.pubkey())),'Failed transaction changed nonpayer state'
    rows.append({'case':row['case'],'signature':sig,'transaction_base64':encoded,'error':status['err'],'before':before,'after':after,'logs':sim.get('logs',[]),'return_data':sim.get('returnData')})
   return rows
  finally:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
def events(row):
 out=[]
 for log in row['logs']:
  if log.startswith('Program data: '):
   data=bytearray(base64.b64decode(log.split(': ',1)[1]));assert data[:8].hex() in ['a537817004b3ca28','15bac4b85be4e1cb'],'Unknown event layout';data[8:16]=bytes(8);out.append(data.hex())
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--surfpool',type=Path,default=ROOT/'work/localnet/surfpool');a=p.parse_args();a.output=a.output.resolve();a.surfpool=a.surfpool.resolve()
 assert subprocess.check_output([str(a.surfpool),'--version'],text=True).strip()=='surfpool 1.6.1'
 for port in [PORT,PORT+1]:
  with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',port))
 a.output.mkdir(parents=True,exist_ok=False);original=a.output/'original.so';candidate=a.output/'candidate.so';original.write_bytes(f.ORIGINAL.read_bytes());candidate.write_bytes(a.candidate.read_bytes())
 wanted=['base','pump-sol-1000000','graduated-3','fund-then-update','fund-then-invalid-new','empty-new','wrong-authority','old-two','stable-recipient-missing','stable-old-two-grouped','matching-quote-3']
 cases=[c for c in f.cases() if c['name'].removeprefix(c['op']+'-') in wanted];script_hash=sha(Path(f.__file__).read_bytes());runner_hash=sha(Path(__file__).read_bytes());fixtures=[prepare(c) for c in cases];(a.output/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
 x=run(original,fixtures,a.surfpool,a.output);y=run(candidate,fixtures,a.surfpool,a.output)
 for rows in [x,y]:
  for row in rows:
   label=row['case']['name'].removeprefix(row['case']['op']+'-');code=6010 if label in ['empty-new','fund-then-invalid-new'] else 6016 if label=='wrong-authority' else None
   expected={'InstructionError':[2 if label=='fund-then-invalid-new' else 1,{'Custom':code}]} if code else None
   assert row['error']==expected,(label,row['error'])
   if label in ['pump-sol-1000000','fund-then-update']:
    key=str(f.AUTH.pubkey());assert row['after'][key]['lamports']-row['before'][key]['lamports']==1000000
   if label=='old-two':
    assert row['after'][str(f.AUTH.pubkey())]['lamports']-row['before'][str(f.AUTH.pubkey())]['lamports']==333300
    assert row['after'][str(f.OTHER.pubkey())]['lamports']-row['before'][str(f.OTHER.pubkey())]['lamports']==666700
 bad=[l['case']['name'] for l,r in zip(x,y) if l['error']!=r['error'] or l['after']!=r['after'] or events(l)!=events(r)]
 assert script_hash==sha(Path(f.__file__).read_bytes()) and runner_hash==sha(Path(__file__).read_bytes())
 report={'scope':'Signed offline sharing updates with captured genuine Pump/AMM CPIs. Exact account/errors comparison; decoded first i64 timestamp excluded from event payload comparison, raw logs retained. Return values retained but not compared. No byte identity claim.','original_sha256':sha(original.read_bytes()),'candidate_sha256':sha(candidate.read_bytes()),'fixture_script_sha256':script_hash,'runner_sha256':runner_hash,'surfpool_sha256':sha(a.surfpool.read_bytes()),'cases':len(cases),'signed_transactions':len(x)+len(y),'mismatches':bad,'original':x,'candidate':y};(a.output/'sharing-update-transactions.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['cases','signed_transactions','mismatches']},indent=2))
 if bad:raise SystemExit(1)
if __name__=='__main__':main()
