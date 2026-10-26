#!/usr/bin/env python3
"""Run an offline Surfpool with captured programs; never sends public RPC requests."""
import argparse
import base64
import hashlib
import json
import shutil
import socket
import struct
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADER = 'BPFLoader2111111111111111111111111111111111'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--surfpool', type=Path, default=ROOT/'work/localnet/surfpool')
    parser.add_argument('--check', action='store_true', help='verify startup and loaded bytes, then stop')
    parser.add_argument('--port', type=int, default=18999)
    parser.add_argument('--studio-port', type=int, default=18488)
    args = parser.parse_args()
    binary = str(args.surfpool.resolve()) if args.surfpool.exists() else shutil.which('surfpool')
    if not binary:
        raise SystemExit('Install Surfpool from https://www.surfpool.run/ first.')
    version = subprocess.check_output([binary, '--version'], text=True).strip()
    if version != 'surfpool 1.6.1':
        raise SystemExit(f'Expected surfpool 1.6.1; found {version}. Review CLI compatibility before changing the pin.')
    for port in (args.port, args.port + 1, args.studio_port):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', port))
    work = ROOT / 'work/surfpool'
    work.mkdir(parents=True, exist_ok=True)
    rpc_url = f'http://127.0.0.1:{args.port}'
    def rpc(method, params=None):
        req = urllib.request.Request(rpc_url, data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode(), headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.load(response)
        if 'error' in result:
            raise RuntimeError(result['error'])
        return result['result']
    with (work/'server.log').open('w') as log:
        process = subprocess.Popen([binary, 'start', '--offline', '--no-deploy', '--no-tui', '--host', '127.0.0.1', '--port', str(args.port), '--ws-port', str(args.port+1), '--studio-port', str(args.studio_port), '--db', ':memory:', '--log-path', str(work/'logs')], cwd=work, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError(f'Surfpool exited. See {work}/server.log')
                try:
                    if rpc('getHealth') == 'ok': break
                except (OSError, RuntimeError): pass
                time.sleep(.2)
            else: raise TimeoutError('Surfpool did not become healthy')
            rows = []
            captures = sorted((ROOT/'evidence/original').glob('*/capture.json')) + sorted((ROOT/'evidence/dependencies').glob('*/capture.json'))
            for capture in captures:
                metadata = json.loads(capture.read_text())
                payload = (capture.parent/'deployed.so').read_bytes()
                assert hashlib.sha256(payload).hexdigest() == metadata['payload_sha256'], capture
                assert payload[:6] == b'\x7fELF\x02\x01'
                extent = struct.unpack_from('<Q', payload, 40)[0] + struct.unpack_from('<H', payload, 58)[0] * struct.unpack_from('<H', payload, 60)[0]
                assert 0 < extent <= len(payload) and not any(payload[extent:]), capture
                elf = payload[:extent]
                address = metadata['program']
                rpc('surfnet_setAccount', [address, {'lamports':10**10, 'owner':LOADER, 'executable':True, 'data':elf.hex()}])
                account = rpc('getAccountInfo', [address, {'encoding':'base64'}])['value']
                assert account['executable'] and account['owner'] == LOADER
                assert base64.b64decode(account['data'][0]) == elf
                rows.append({'name':capture.parent.name,'program':address,'elf_bytes':len(elf),'elf_sha256':hashlib.sha256(elf).hexdigest(),'capture_sha256':metadata['payload_sha256']})
            fixture_rows = []
            lane = ROOT/'research/imported-lab/analysis/pump_fun'
            configs = json.loads((lane/'config-snapshot.json').read_text())['accounts']
            pool = json.loads((lane/'amm-v2-trade-fixture.json').read_text())['accounts']
            for entry in configs + list(pool.values()):
                data = base64.b64decode(entry['data_base64'])
                assert hashlib.sha256(data).hexdigest() == entry['data_sha256']
                rpc('surfnet_setAccount', [entry['address'], {'lamports':entry['lamports'], 'owner':entry['owner'], 'executable':entry.get('executable',False), 'data':data.hex()}])
                actual = rpc('getAccountInfo', [entry['address'], {'encoding':'base64'}])['value']
                assert base64.b64decode(actual['data'][0]) == data
                assert actual['lamports'] == entry['lamports'] and actual['owner'] == entry['owner']
                fixture_rows.append({'address':entry['address'],'sha256':entry['data_sha256']})
            report = {'surfpool_version':version, 'rpc':rpc_url, 'offline':True, 'programs':rows, 'account_fixtures':fixture_rows, 'scope':'Captured original ELFs and dependency ELFs under legacy loader, captured configuration and one AMM pool; startup and byte readback only. No transactions, reconstruction identity, or complete chain snapshot established.'}
            (work/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(report, indent=2), flush=True)
            if not args.check:
                print(f'Studio: http://127.0.0.1:{args.studio_port} — Ctrl-C to stop', flush=True)
                process.wait()
        except KeyboardInterrupt:
            pass
        finally:
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

if __name__ == '__main__':
    main()
