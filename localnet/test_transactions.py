#!/usr/bin/env python3
"""Replay captured fixtures and signed transactions in isolated offline Surfpool instances."""
import argparse
import hashlib
import json
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--surfpool',type=Path,default=ROOT/'work/localnet/surfpool')
    parser.add_argument('--docs-checkout',type=Path,default=ROOT/'work/localnet/pump-public-docs')
    parser.add_argument('--output',type=Path,default=ROOT/'work/localnet'/('transactions-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')))
    args = parser.parse_args()
    # Existing harnesses own these loopback ports; never reuse another process.
    for port in (19831,19832,19851,19852,19871,19872,19891,19892):
        with socket.socket() as sock: sock.bind(('127.0.0.1',port))
    subprocess.run([sys.executable,str(ROOT/'scripts/verify_imported_lab.py'),
        '--docs-checkout',str(args.docs_checkout.resolve()),'--output',str(args.output.resolve()),
        '--surfpool',str(args.surfpool.resolve())],check=True,cwd=ROOT)
    output = args.output.resolve()
    receipts = output/'lab/analysis/pump_fun'
    names = ['admin-signed-surfpool','amm-buy-v2-signed-surfpool','curve-create-v2-signed-surfpool',
        'curve-fresh-trades-v3-signed-surfpool','curve-completion-signed-surfpool',
        'curve-migrate-v2-signed-surfpool','post-migration-amm-v2-signed-surfpool','fees-withdraw-signed-surfpool']
    rows=[]; transactions={}
    def collect(value):
        if isinstance(value,dict):
            if 'transaction_base64' in value:
                encoded=value['transaction_base64']
                transactions[encoded]={'label':value.get('label'),'committed_error':value.get('committed_error')}
            for item in value.values(): collect(item)
        elif isinstance(value,list):
            for item in value: collect(item)
    for name in names:
        path=receipts/(name+'.json'); raw=path.read_bytes(); collect(json.loads(raw))
        rows.append({'path':str(path.relative_to(output)),'sha256':hashlib.sha256(raw).hexdigest()})
    assert transactions, 'No signed transaction receipts found'
    summary={'created_at_utc':datetime.now(timezone.utc).isoformat(),'surfpool_version':'1.6.1',
        'receipt_files':rows,'unique_signed_transactions':len(transactions),
        'successful_transactions':sum(x['committed_error'] is None for x in transactions.values()),
        'expected_rejections':sum(x['committed_error'] is not None for x in transactions.values()),
        'all_fresh_receipt_checks_passed':True,
        'scope':'Offline original-program fixture tests only. Synthetic signers and authority substitutions; no full byte-identity or complete historical state claim. Mayhem trade execution is not covered by the imported lifecycle suite.'}
    (output/'transaction-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__': main()
