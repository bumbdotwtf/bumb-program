#!/usr/bin/env python3
"""Normally signed, offline Surfpool buyback initialization, configuration and sweeping comparisons."""
import argparse,base64,hashlib,json,socket,struct,subprocess,sys,time,urllib.request
from pathlib import Path
from solders.hash import Hash
from solders.instruction import AccountMeta,Instruction
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit
from solders.system_program import transfer,TransferParams
from solders.pubkey import Pubkey
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fees_buyback_differential as f
PORT=20001
sha=lambda b:hashlib.sha256(b).hexdigest()

class RecordingVM:
    def __init__(self,vm): self.vm=vm;self.accounts={};self.transaction=None
    def with_transaction_history(self,n):self.vm.with_transaction_history(n);return self
    def __getattr__(self,name): return getattr(self.vm,name)
    def set_account(self,key,account):
        self.accounts[str(key)]={'lamports':account.lamports,'data':account.data.hex(),'owner':str(account.owner),'executable':account.executable}
        return self.vm.set_account(key,account)
    def send_transaction(self,transaction):
        self.transaction=transaction
        return self.vm.send_transaction(transaction)

def prepare(c):
    original_type=f.LiteSVM;recorded=[]
    def factory():
        vm=RecordingVM(original_type());recorded.append(vm);return vm
    f.LiteSVM=factory
    try:receipt=f.run(c)
    finally:f.LiteSVM=original_type
    vm=recorded[0];vault=receipt['vault'];token=f.TOKEN2022 if c.get('token2022') else f.TOKEN;mint=f.WSOL if c.get('native',True) else f.MINT
    ata=Pubkey.find_program_address([bytes(Pubkey.from_string(vault)),bytes(token),bytes(mint)],f.ATA)[0]
    return {'case':c,'vault':vault,'vault_ata':str(ata),'accounts':vm.accounts,'transaction_base64':base64.b64encode(bytes(vm.transaction)).decode(),'litesvm_error':receipt['error']}

def run(binary,cases,surfpool,output):
    def rpc(method,params=None):
        req=urllib.request.Request(f'http://127.0.0.1:{PORT}',data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=60) as response: result=json.load(response)
        if 'error' in result: raise RuntimeError((method,result['error']))
        return result['result']
    def get(key):
        a=rpc('getAccountInfo',[str(key),{'encoding':'base64'}])['value']
        return None if a is None else {'lamports':a['lamports'],'owner':a['owner'],'data':base64.b64decode(a['data'][0]).hex()}
    with (output/(binary.stem+'.log')).open('w') as log:
        process=subprocess.Popen([str(surfpool),'start','--offline','--no-deploy','--no-tui','--no-studio','--host','127.0.0.1','--port',str(PORT),'--ws-port',str(PORT+1),'--airdrop-amount','0','--db',':memory:'],cwd=output,stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                if process.poll() is not None: raise RuntimeError('Surfpool terminated')
                try:
                    if rpc('getHealth')=='ok':break
                except OSError:pass
                time.sleep(.1)
            else:raise TimeoutError('Surfpool startup')
            programs=[(f.PROGRAM,binary)]+[(key,ROOT/f'evidence/dependencies/{name}/deployed.so') for name,key in [('spl_token',f.TOKEN),('spl_token_2022',f.TOKEN2022),('associated_token',f.ATA)]]
            for key,path in programs:
                blob=path.read_bytes();extent=struct.unpack_from('<Q',blob,40)[0]+struct.unpack_from('<H',blob,58)[0]*struct.unpack_from('<H',blob,60)[0]
                assert not any(blob[extent:]),'Nonzero data after ELF section table'
                rpc('surfnet_setAccount',[str(key),{'lamports':10**10,'data':blob[:extent].hex(),'owner':'BPFLoader2111111111111111111111111111111111','executable':True}])
            results=[]
            for i,row in enumerate(cases):
                for key,account in row['accounts'].items():
                    if row['case'].get('carry_vault') and key in [row['vault'],row['vault_ata']]:continue
                    rpc('surfnet_setAccount',[key,account])
                before={key:get(key) for key in row['accounts']}
                original=Transaction.from_bytes(base64.b64decode(row['transaction_base64']));msg=original.message;h=msg.header;keys=msg.account_keys
                def writable(index):
                    return index<h.num_required_signatures-h.num_readonly_signed_accounts if index<h.num_required_signatures else index<len(keys)-h.num_readonly_unsigned_accounts
                instructions=[set_compute_unit_limit(1400000-i)]
                if row['case'].get('fund_transfer'):
                    key=row['vault']
                    instructions.append(transfer(TransferParams(from_pubkey=f.PAYER.pubkey(),to_pubkey=Pubkey.from_string(key),lamports=row['case']['fund_transfer'])))
                for ix in msg.instructions:
                    payload=bytes(ix.data)
                    if row['case'].get('set_authority_to_test_key'):payload=payload[:9]+bytes(f.AUTH.pubkey())
                    instructions.append(Instruction(keys[ix.program_id_index],payload,[AccountMeta(keys[n],n<h.num_required_signatures,writable(n)) for n in ix.accounts]))
                signers=[kp for kp in [f.PAYER,f.AUTH,f.OTHER] if kp.pubkey() in keys[:h.num_required_signatures]]
                tx=Transaction.new_signed_with_payer(instructions,f.PAYER.pubkey(),signers,Hash.from_string(rpc('getLatestBlockhash')['value']['blockhash']))
                assert all(tx.verify_with_results())
                encoded=base64.b64encode(bytes(tx)).decode()
                sim=rpc('simulateTransaction',[encoded,{'encoding':'base64','sigVerify':True}])['value']
                sig=rpc('sendTransaction',[encoded,{'encoding':'base64','skipPreflight':True}])
                for _ in range(100):
                    status=rpc('getSignatureStatuses',[[sig]])['value'][0]
                    if status is not None:break
                    time.sleep(.05)
                else:raise TimeoutError('Transaction confirmation')
                assert sim['err']==status['err']
                after={key:get(key) for key in row['accounts']}
                if status['err']:
                    assert all(before[k]==after[k] for k in before if k!=str(f.PAYER.pubkey())),'Failed tx changed non-fee-payer state'
                results.append({'case':row['case'],'signature':sig,'transaction_base64':encoded,'error':status['err'],'before':before,'after':after,'logs':sim.get('logs',[]),'vault':row['vault']})
            return results
        finally:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()

def normalize(row):
    # Independent Surfpool wall clocks differ. Exclude only BuybackVault.last_claimed.
    value=json.loads(json.dumps(row['after']));disc=hashlib.sha256(b'account:BuybackVault').digest()[:8]
    for account in value.values():
        if not account:continue
        data=bytearray.fromhex(account['data'])
        if data[:8]==disc and len(data)>=72:data[64:72]=bytes(8);account['data']=data.hex()
    return value

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--surfpool',type=Path,default=ROOT/'work/localnet/surfpool');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output=a.output.resolve();a.surfpool=a.surfpool.resolve()
    assert subprocess.check_output([str(a.surfpool),'--version'],text=True).strip()=='surfpool 1.6.1'
    for port in [PORT,PORT+1]:
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',port))
    a.output.mkdir(parents=True,exist_ok=False)
    original=a.output/'original.so';candidate=a.output/'candidate.so';original.write_bytes((ROOT/'evidence/original/pump_fees/deployed.so').read_bytes());candidate.write_bytes(a.candidate.read_bytes())
    cases=[{'name':'initialize-native','op':'initialize_buyback'},{'name':'initialize-token2022','op':'initialize_buyback','native':False,'token2022':True},{'name':'initialize-bad-index','op':'initialize_buyback','index':8},{'name':'initialize-bad-mint-owner','op':'initialize_buyback','mint_owner':str(f.PROGRAM)},{'name':'update-authority','op':'update_buyback_authority'},{'name':'update-authority-reject','op':'update_buyback_authority','wrong_authority':True},{'name':'update-rate','op':'update_buyback_claim_rate_limit','new_rate':-1},{'name':'sweep-native','op':'sweep_buyback'},{'name':'sweep-zero','op':'sweep_buyback','amount':0},{'name':'sweep-native-and-tokens','op':'sweep_buyback','tokens':1000000},{'name':'sweep-token','op':'sweep_buyback','native':False,'tokens':1000000},{'name':'sweep-token2022','op':'sweep_buyback','native':False,'token2022':True,'tokens':1000000},{'name':'sweep-cooldown','op':'sweep_buyback','last':2**63-1},{'name':'sweep-overflow','op':'sweep_buyback','total':2**64-1},{'name':'sweep-authority-reject','op':'sweep_buyback','wrong_authority':True}]
    cases += [{'name':'sequence-initialize','op':'initialize_buyback'},{'name':'sequence-authorize','op':'update_buyback_authority','carry_vault':True,'set_authority_to_test_key':True},{'name':'sequence-fund-sweep','op':'sweep_buyback','carry_vault':True,'fund_transfer':1000000}]
    fixture_hash=sha(Path(f.__file__).read_bytes());source_hash=sha(Path(__file__).read_bytes())
    fixtures=[prepare(c) for c in cases];(a.output/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    x=run(original,fixtures,a.surfpool,a.output);y=run(candidate,fixtures,a.surfpool,a.output)
    (a.output/'raw-transactions.json').write_text(json.dumps({'original':x,'candidate':y},indent=2)+'\n')
    expected_errors={name:{'InstructionError':[1,{'Custom':code}]} for name,code in [('initialize-bad-index',6026),('initialize-bad-mint-owner',3007),('update-authority-reject',6016),('sweep-cooldown',6027),('sweep-overflow',6025),('sweep-authority-reject',6016)]}
    assert all(row['error']==expected_errors.get(row['case']['name']) for row in x),'Original behavior changed'
    assert fixture_hash==sha(Path(f.__file__).read_bytes()),'Fixture script changed during run'
    assert source_hash==sha(Path(__file__).read_bytes()),'Runner changed during run'
    for rows in [x,y]:
        sequence=rows[-3:];states=[]
        for row in sequence:
            account=row['after'][row['vault']];data=bytes.fromhex(account['data'])
            states.append((account['lamports'],data[8:40].hex(),int.from_bytes(data[40:48],'little'),int.from_bytes(data[64:72],'little',signed=True)))
        assert states[0]==(2338560,bytes(32).hex(),0,0)
        assert states[1]==(2338560,bytes(f.AUTH.pubkey()).hex(),0,0)
        assert states[2][0:3]==(2338560,bytes(f.AUTH.pubkey()).hex(),1000000) and states[2][3]>0
        key=str(f.OTHER.pubkey())
        assert sequence[2]['after'][key]['lamports']-sequence[2]['before'][key]['lamports']==1000000
    mismatches=[l['case']['name'] for l,r in zip(x,y) if l['error']!=r['error'] or normalize(l)!=normalize(r) or [v for v in l['logs'] if v.startswith('Program data:')]!=[v for v in r['logs'] if v.startswith('Program data:')]]
    report={'scope':'Normally signed offline Surfpool buyback initialization, configuration and sweeping with synthetic accounts. Errors, owner, lamports and data compared except BuybackVault.last_claimed; event payloads compared, raw timestamps and logs retained. No complete source or byte identity claim.','original_sha256':sha(original.read_bytes()),'candidate_sha256':sha(candidate.read_bytes()),'surfpool_sha256':sha(a.surfpool.read_bytes()),'fixture_script_sha256':fixture_hash,'runner_sha256':source_hash,'dependency_sha256':{name:sha((ROOT/f'evidence/dependencies/{name}/deployed.so').read_bytes()) for name in ['spl_token','spl_token_2022','associated_token']},'cases':len(cases),'signed_transactions':len(x)+len(y),'mismatches':mismatches,'original':x,'candidate':y}
    (a.output/'buyback-transactions.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['cases','signed_transactions','mismatches','original_sha256','candidate_sha256']},indent=2))
    if mismatches:raise SystemExit(1)
if __name__=='__main__':main()
