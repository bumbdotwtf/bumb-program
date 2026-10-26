#!/usr/bin/env python3
"""Normally signed offline Surfpool original/candidate social V2 claim checks."""
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
sys.path.insert(0, str(ROOT / 'scripts'))
import fees_social_claim_v2_differential as fixtures
from social_transactions import RecordingVM
PORT = 19971
COMPUTE = Pubkey.from_string('ComputeBudget111111111111111111111111111111')
DEPENDENCIES = [('spl_token', fixtures.TOKEN), ('spl_token_2022', fixtures.TOKEN22),
                ('associated_token', fixtures.ATA)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(case):
    original_type = fixtures.LiteSVM
    recorded = []
    def factory():
        vm = RecordingVM(original_type())
        recorded.append(vm)
        return vm
    fixtures.LiteSVM = factory
    try:
        receipt = fixtures.run(case)
    finally:
        fixtures.LiteSVM = original_type
    vm = recorded[0]
    return {'case': case, 'accounts': vm.accounts,
            'transaction_base64': base64.b64encode(bytes(vm.transaction)).decode(),
            'litesvm_error': receipt['error']}


def run(binary, cases, surfpool, output):
    def rpc(method, params=None):
        request = urllib.request.Request(f'http://127.0.0.1:{PORT}', data=json.dumps(
            {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or []}).encode(),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
        if 'error' in result:
            raise RuntimeError((method, result['error']))
        return result['result']

    def get(key):
        value = rpc('getAccountInfo', [key, {'encoding': 'base64'}])['value']
        return None if value is None else {'lamports': value['lamports'], 'owner': value['owner'],
            'executable': value['executable'], 'data': base64.b64decode(value['data'][0]).hex()}

    with (output / (binary.stem + '.log')).open('w') as log:
        process = subprocess.Popen([str(surfpool), 'start', '--offline', '--no-deploy', '--no-tui',
            '--no-studio', '--host', '127.0.0.1', '--port', str(PORT), '--ws-port', str(PORT + 1),
            '--airdrop-amount', '0', '--db', ':memory:'], cwd=output, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError('Surfpool terminated during startup')
                try:
                    if rpc('getHealth') == 'ok':
                        break
                except OSError:
                    pass
                time.sleep(.1)
            else:
                raise TimeoutError('Surfpool startup')
            programs = [(fixtures.PROGRAM, binary)] + [(key, ROOT / f'evidence/dependencies/{name}/deployed.so')
                        for name, key in DEPENDENCIES]
            for key, path in programs:
                blob = path.read_bytes()
                extent = struct.unpack_from('<Q', blob, 40)[0] + struct.unpack_from('<H', blob, 58)[0] * struct.unpack_from('<H', blob, 60)[0]
                if any(blob[extent:]):
                    raise AssertionError(f'Nonzero bytes after ELF section table: {path}')
                rpc('surfnet_setAccount', [str(key), {'lamports': 10**10, 'data': blob[:extent].hex(),
                    'owner': 'BPFLoader2111111111111111111111111111111111', 'executable': True}])
            results = []
            for index, case in enumerate(cases):
                for key, account in case['accounts'].items():
                    rpc('surfnet_setAccount', [key, account])
                before = {key: get(key) for key in case['accounts']}
                source = Transaction.from_bytes(base64.b64decode(case['transaction_base64']))
                message = source.message
                header, keys = message.header, message.account_keys
                def writable(n):
                    if n < header.num_required_signatures:
                        return n < header.num_required_signatures - header.num_readonly_signed_accounts
                    return n < len(keys) - header.num_readonly_unsigned_accounts
                # The saved fixture already has a compute-budget instruction.
                # Replace it, rather than submitting duplicate limit settings.
                instructions = [set_compute_unit_limit(1_400_000 - index)]
                for ix in message.instructions:
                    if keys[ix.program_id_index] == COMPUTE:
                        continue
                    instructions.append(Instruction(keys[ix.program_id_index], bytes(ix.data),
                        [AccountMeta(keys[n], n < header.num_required_signatures, writable(n)) for n in ix.accounts]))
                signers = [kp for kp in [fixtures.PAYER, fixtures.AUTH, fixtures.OTHER]
                           if kp.pubkey() in keys[:header.num_required_signatures]]
                tx = Transaction.new_signed_with_payer(instructions, fixtures.PAYER.pubkey(), signers,
                    Hash.from_string(rpc('getLatestBlockhash')['value']['blockhash']))
                if not all(tx.verify_with_results()):
                    raise AssertionError('Transaction signatures failed verification')
                encoded = base64.b64encode(bytes(tx)).decode()
                simulation = rpc('simulateTransaction', [encoded, {'encoding': 'base64', 'sigVerify': True}])['value']
                signature = rpc('sendTransaction', [encoded, {'encoding': 'base64', 'skipPreflight': True}])
                for _ in range(100):
                    status = rpc('getSignatureStatuses', [[signature]])['value'][0]
                    if status is not None:
                        break
                    time.sleep(.05)
                else:
                    raise TimeoutError('Transaction confirmation')
                if simulation['err'] != status['err']:
                    raise AssertionError('Simulation and committed transaction error differ')
                after = {key: get(key) for key in case['accounts']}
                if status['err']:
                    assert all(before[key] == after[key] for key in before if key != str(fixtures.PAYER.pubkey())), 'Rejected transaction mutated non-fee-payer state'
                results.append({'case': case['case'], 'signature': signature, 'transaction_base64': encoded,
                    'signature_verification': True, 'error': status['err'], 'before': before, 'after': after,
                    'logs': simulation.get('logs', []), 'return_data': simulation.get('returnData'),
                    'simulation': simulation})
            return results
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def normalized(row):
    result = {'error': row['error'], 'before': row['before'], 'after': json.loads(json.dumps(row['after']))}
    social_discriminator = hashlib.sha256(b'account:SocialFeePda').digest()[:8]
    for account in result['after'].values():
        if not account:
            continue
        data = bytearray.fromhex(account['data'])
        if data[:8] == social_discriminator and len(data) >= 14:
            offset = 14 + int.from_bytes(data[10:14], 'little') + 1 + 8
            if len(data) >= offset + 8:
                data[offset:offset + 8] = bytes(8)
                account['data'] = data.hex()
    events = []
    for line in row['logs']:
        if line.startswith('Program data: '):
            blob = bytearray(base64.b64decode(line[len('Program data: '):]))
            # SocialFeePdaClaimed event: discriminator[8], timestamp i64[8].
            assert blob[:8] == hashlib.sha256(b'event:SocialFeePdaClaimed').digest()[:8]
            blob[8:16] = bytes(8)
            events.append(blob.hex())
    result['events_except_timestamp'] = events
    returned = row['return_data']
    if returned:
        data = bytearray(base64.b64decode(returned['data'][0]))
        if data and data[0] == 1:
            data[1:9] = bytes(8)
        result['return_except_timestamp'] = {'programId': returned['programId'], 'data': data.hex()}
    else:
        result['return_except_timestamp'] = None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--surfpool', type=Path, default=ROOT / 'work/localnet/surfpool')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output, args.surfpool = args.output.resolve(), args.surfpool.resolve()
    if subprocess.check_output([str(args.surfpool), '--version'], text=True).strip() != 'surfpool 1.6.1':
        raise RuntimeError('Expected pinned Surfpool 1.6.1')
    for port in [PORT, PORT + 1]:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', port))
    args.output.mkdir(parents=True, exist_ok=False)
    original, candidate = args.output / 'original.so', args.output / 'candidate.so'
    original.write_bytes(fixtures.ORIGINAL.read_bytes())
    candidate.write_bytes(args.candidate.read_bytes())
    names = ['native-base', 'native-no-atas', 'native-tokens-only', 'usdc', 'arbitrary', 'usdc-token22',
             'usdc-create-destination', 'usdc-no-destination', 'usdc-zero', 'flags-2',
             'usdc-source-mint', 'recipient-social-stable']
    available = {case['name']: case for case in fixtures.cases()}
    cases = [dict(available[name]) for name in names]
    cases.append({'name': 'stable-future-cooldown', 'quote': str(fixtures.USDC), 'last': 2**64 - 1})
    fixture_hash, runner_hash = sha(Path(fixtures.__file__)), sha(Path(__file__))
    prepared = [prepare(case) for case in cases]
    (args.output / 'fixtures.json').write_text(json.dumps(prepared, indent=2) + '\n')
    left = run(original, prepared, args.surfpool, args.output)
    right = run(candidate, prepared, args.surfpool, args.output)
    (args.output / 'raw-transactions.json').write_text(json.dumps({'original': left, 'candidate': right}, indent=2) + '\n')
    expected = {'usdc-no-destination': {'InstructionError': [1, 'PrivilegeEscalation']},
                'flags-2': {'InstructionError': [1, {'Custom': 6021}]},
                'usdc-source-mint': {'InstructionError': [1, {'Custom': 6030}]}}
    unexpected = [row['case']['name'] for row in left if row['error'] != expected.get(row['case']['name'])]
    mismatches = [x['case']['name'] for x, y in zip(left, right) if normalized(x) != normalized(y)]
    assert fixture_hash == sha(Path(fixtures.__file__)), 'Fixture script changed during run'
    assert runner_hash == sha(Path(__file__)), 'Runner changed during run'
    report = {'scope': 'Normally signed offline Surfpool social V2 claims. Synthetic accounts; errors, complete fixture-account states, events and return values compared except decoded wall-clock timestamps. Raw state/logs/return retained. No full-program byte identity claim.',
        'original_sha256': sha(original), 'candidate_sha256': sha(candidate), 'surfpool_sha256': sha(args.surfpool),
        'fixture_script_sha256': fixture_hash, 'runner_sha256': runner_hash,
        'dependency_sha256': {name: sha(ROOT / f'evidence/dependencies/{name}/deployed.so') for name, _ in DEPENDENCIES},
        'cases': len(cases), 'signed_transactions': len(left) + len(right), 'mismatches': mismatches,
        'unexpected_original_errors': unexpected, 'original': left, 'candidate': right}
    (args.output / 'social-v2-transactions.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['cases', 'signed_transactions', 'mismatches', 'unexpected_original_errors', 'original_sha256', 'candidate_sha256']}, indent=2))
    if mismatches or unexpected:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
