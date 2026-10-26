import base64
import json
import pathlib
import struct
import urllib.request

from solders.account import Account
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.litesvm import LiteSVM
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.transaction_metadata import FailedTransactionMetadata

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM = Pubkey.default()
PAYER = Keypair.from_seed(bytes([19]) * 32)


def pk(key):
    return key if isinstance(key, Pubkey) else Pubkey.from_string(key)


def meta(key, writable=False, signer=False):
    return AccountMeta(pk(key), signer, writable)


def token_account(mint, amount, owner=PAYER.pubkey()):
    data = bytearray(165)
    data[:32] = bytes(pk(mint))
    data[32:64] = bytes(owner)
    struct.pack_into("<Q", data, 64, amount)
    data[108] = 1
    return Account(2039280, bytes(data), TOKEN)


def ata(mint):
    return Pubkey.find_program_address([bytes(PAYER.pubkey()), bytes(TOKEN), bytes(pk(mint))], ASSOCIATED)[0]


def account_json(acc):
    return {"lamports": acc.lamports, "owner": str(acc.owner), "executable": acc.executable,
            "rentEpoch": acc.rent_epoch, "data": [base64.b64encode(acc.data).decode(), "base64"]}


def vm_new():
    vm = LiteSVM().with_sigverify(False).with_blockhash_check(False)
    vm.airdrop(PAYER.pubkey(), 10**10)
    return vm


def load_snapshot(vm, path):
    snapshot = json.loads(path.read_text())
    for key, a in snapshot["accounts"].items():
        if a and not a["executable"]:
            vm.set_account(pk(key), Account(a["lamports"], base64.b64decode(a["data"][0]),
                                           pk(a["owner"]), False, a["rentEpoch"]))
    return snapshot


def simulate(vm, instructions):
    tx = Transaction.new_signed_with_payer(instructions, PAYER.pubkey(), [PAYER], vm.latest_blockhash())
    result = vm.simulate_transaction(tx)
    failed = isinstance(result, FailedTransactionMetadata)
    m = result.meta() if failed else result.meta()
    record = {"success": not failed, "error": str(result.err()) if failed else None,
              "logs": m.logs(), "cu": m.compute_units_consumed(),
              "return_data": bytes(m.return_data().data).hex(),
              "inner_instructions": json.loads(m.to_json())["inner_instructions"],
              "post_accounts": {} if failed else {str(k): account_json(v) for k, v in result.post_accounts()}}
    return record, tx


def local_rpc(method, params):
    # Deliberately fixed loopback destination. Cannot send to a chain endpoint.
    req = urllib.request.Request("http://127.0.0.1:18999",
                                 data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),
                                 headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result["result"]


def surf_set(key, account):
    if isinstance(account, Account):
        account = account_json(account)
    return local_rpc("surfnet_setAccount", [str(key), {"lamports":account["lamports"], "owner":account["owner"],
                       "executable":account.get("executable",False),
                       "data":base64.b64decode(account["data"][0]).hex()}])
