#!/usr/bin/env python3
"""Signed offline Surfpool original/candidate Mayhem admin differential checks."""
import argparse
import base64
import hashlib
import json
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from solders.compute_budget import set_compute_unit_limit
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.transaction import Transaction

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import mayhem_validate_admin as fixtures
PORT=19931

def sha(data): return hashlib.sha256(data).hexdigest()

def run(binary, cases, surfpool, output):
    def rpc(method, params=None):
        request=urllib.request.Request(f'http://127.0.0.1:{PORT}',data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=60) as response: result=json.load(response)
        if 'error' in result: raise RuntimeError((method,result['error']))
        return result['result']
    def put(key,lamports,data,owner,executable=False):
        rpc('surfnet_setAccount',[str(key),{'lamports':lamports,'data':data.hex(),'owner':str(owner),'executable':executable}])
    def get(key):
        a=rpc('getAccountInfo',[str(key),{'encoding':'base64'}])['value']
        return None if a is None else {'data':base64.b64decode(a['data'][0]).hex(),'lamports':a['lamports'],'owner':a['owner']}
    with (output/(binary.stem+'.log')).open('w') as log:
        process=subprocess.Popen([str(surfpool),'start','--offline','--no-deploy','--no-tui','--no-studio','--host','127.0.0.1','--port',str(PORT),'--ws-port',str(PORT+1),'--airdrop-amount','0','--db',':memory:'],cwd=output,stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                if process.poll() is not None: raise RuntimeError('Surfpool terminated')
                try:
                    if rpc('getHealth')=='ok': break
                except OSError: pass
                time.sleep(.1)
            else: raise TimeoutError('Surfpool startup')
            blob=binary.read_bytes()
            extent=struct.unpack_from('<Q',blob,40)[0]+struct.unpack_from('<H',blob,58)[0]*struct.unpack_from('<H',blob,60)[0]
            assert not any(blob[extent:])
            put(fixtures.PROGRAM,10**10,blob[:extent],'BPFLoader2111111111111111111111111111111111',True)
            results=[]
            for i,c in enumerate(cases):
                for key in [fixtures.ADMIN.pubkey(),fixtures.PAYER.pubkey(),fixtures.OTHER,fixtures.EVENT]: put(key,10**10,b'',Pubkey.default())
                kind=c.get('kind','ok'); key=fixtures.OTHER if kind=='wrong_pda' else fixtures.GLOBAL
                data=bytes.fromhex(c['data'])
                owner=Pubkey.default() if kind=='wrong_owner' else fixtures.PROGRAM
                put(key,10**9,data,owner)
                metas=[AccountMeta(fixtures.ADMIN.pubkey(),kind!='unsigned_admin',kind!='readonly_admin'),AccountMeta(key,False,kind!='readonly_global'),AccountMeta(Pubkey.default(),False,False),AccountMeta(fixtures.EVENT,False,False),AccountMeta(fixtures.PROGRAM,False,False)]
                payload=hashlib.sha256(('global:'+c['op']).encode()).digest()[:8]+bytes.fromhex(c.get('args',''))
                signers=[fixtures.PAYER]+([fixtures.ADMIN] if kind!='unsigned_admin' else [])
                tx=Transaction.new_signed_with_payer([set_compute_unit_limit(1000000+i),Instruction(fixtures.PROGRAM,payload,metas)],fixtures.PAYER.pubkey(),signers,Hash.from_string(rpc('getLatestBlockhash')['value']['blockhash']))
                assert all(tx.verify_with_results())
                encoded=base64.b64encode(bytes(tx)).decode();before=get(key)
                simulation=rpc('simulateTransaction',[encoded,{'encoding':'base64','sigVerify':True}])['value']
                signature=rpc('sendTransaction',[encoded,{'encoding':'base64','skipPreflight':True}])
                for _ in range(100):
                    status=rpc('getSignatureStatuses',[[signature]])['value'][0]
                    if status is not None: break
                    time.sleep(.05)
                else: raise TimeoutError('Transaction status')
                assert status['err']==simulation['err']
                after=get(key)
                if status['err'] is not None: assert before==after, 'Failed transaction mutated account'
                results.append({'case':c,'signature':signature,'transaction_base64':encoded,'error':status['err'],'before':before,'after':after,'admin_lamports_delta':get(fixtures.ADMIN.pubkey())['lamports']-10**10,'payer_lamports_delta':get(fixtures.PAYER.pubkey())['lamports']-10**10,'logs':simulation.get('logs',[])})
            return results
        finally:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill();process.wait()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--surfpool',type=Path,default=ROOT/'work/localnet/surfpool')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output=a.output.resolve();a.surfpool=a.surfpool.resolve()
    assert subprocess.check_output([str(a.surfpool),'--version'],text=True).strip()=='surfpool 1.6.1'
    for port in [PORT,PORT+1]:
        with socket.socket() as sock: sock.bind(('127.0.0.1',port))
    a.output.mkdir(parents=True,exist_ok=False)
    original=a.output/'original.so';candidate=a.output/'candidate.so'
    original.write_bytes((ROOT/'evidence/original/mayhem/deployed.so').read_bytes());candidate.write_bytes(a.candidate.read_bytes())
    # Freeze fixtures at invocation: ongoing reconstruction work may extend them later.
    rows=[c for c in fixtures.cases() if c['op'] in fixtures.OPS and (c['name'].endswith('-state-0') or c['name'].endswith('-state-1') or c.get('kind') in ['unsigned_admin','wrong_owner','readonly_global','wrong_pda'])]
    x=run(original,rows,a.surfpool,a.output);y=run(candidate,rows,a.surfpool,a.output)
    fields=['error','after','admin_lamports_delta','payer_lamports_delta']
    mismatches=[l['case']['name'] for l,r in zip(x,y) if any(l[k]!=r[k] for k in fields)]
    report={'scope':'Signed offline transactions comparing ten Mayhem admin handlers over synthetic fixtures. Account state, errors and balance deltas compared. Logs retained but timestamp-sensitive events not compared. Not Mayhem trades or full program byte identity.','original_sha256':sha(original.read_bytes()),'candidate_sha256':sha(candidate.read_bytes()),'fixtures_script_sha256':sha(Path(fixtures.__file__).read_bytes()),'surfpool_sha256':sha(a.surfpool.read_bytes()),'cases':len(rows),'signed_transactions':len(x)+len(y),'mismatches':mismatches,'original':x,'candidate':y}
    (a.output/'mayhem-transactions.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['original_sha256','candidate_sha256','cases','signed_transactions','mismatches']},indent=2))
    if mismatches: raise SystemExit(1)
if __name__=='__main__': main()
