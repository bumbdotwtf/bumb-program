"""Signed, fund-moving Pump Fees Withdraw on an isolated synthetic WSOL vault."""

import base64
import hashlib
import json
import struct
import subprocess
import time
import urllib.error
from pathlib import Path

from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction

import pump_fun_admin_surfpool as local


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/pump_fun/fees-withdraw-signed-surfpool.json"
PORT = 19871
FEES = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM = Pubkey.default()
LOADER = Pubkey.from_string("BPFLoader2111111111111111111111111111111111")
USER = Keypair.from_seed(bytes([221]) * 32)
OUTSIDER = Keypair.from_seed(bytes([222]) * 32)
INITIAL_VAULT_RAW = 1_000_000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get(key):
    value = local.rpc("getAccountInfo", [str(key), {"encoding": "base64"}])["value"]
    if value is None:
        return None
    data = base64.b64decode(value["data"][0])
    return {"lamports": value["lamports"], "owner": value["owner"],
            "data": data}


def snapshot(addresses):
    state = {}
    for name, key in addresses.items():
        item = get(key)
        if item is None:
            state[name] = None
            continue
        row = {"lamports": item["lamports"], "owner": item["owner"],
               "data_sha256": sha(item["data"]),
               "data_base64": base64.b64encode(item["data"]).decode()}
        if item["owner"] == str(TOKEN) and len(item["data"]) == 165:
            row["token_amount"] = struct.unpack_from("<Q", item["data"], 64)[0]
        state[name] = row
    return state


def send(label, instruction, payer, addresses, success):
    blockhash = Hash.from_string(local.rpc("getLatestBlockhash")["value"]["blockhash"])
    tx = Transaction.new_signed_with_payer([instruction], payer.pubkey(),
                                            [payer], blockhash)
    assert all(tx.verify_with_results())
    encoded = base64.b64encode(bytes(tx)).decode()
    before = snapshot(addresses)
    payer_before = get(payer.pubkey())["lamports"]
    simulation = local.rpc("simulateTransaction", [encoded,
        {"encoding": "base64", "sigVerify": True}])["value"]
    assert (simulation["err"] is None) == success, (
        label, simulation["err"], (simulation.get("logs") or [])[-25:])
    signature = local.rpc("sendTransaction", [encoded,
        {"encoding": "base64", "skipPreflight": not success}])
    status = None
    for _ in range(100):
        status = local.rpc("getSignatureStatuses", [[signature]])["value"][0]
        if status is not None:
            break
        time.sleep(.05)
    assert status is not None and status["err"] == simulation["err"]
    after = snapshot(addresses)
    if not success:
        assert before == after
    return {"label": label, "signature": signature,
            "transaction_base64": encoded,
            "simulation_error": simulation["err"],
            "committed_error": status["err"],
            "units_consumed": simulation.get("unitsConsumed"),
            "payer_lamports_delta": get(payer.pubkey())["lamports"] - payer_before,
            "before": before, "after": after,
            "log_tail": (simulation.get("logs") or [])[-20:]}


def main():
    local.PORT = PORT
    local.RPC = f"http://127.0.0.1:{PORT}"
    manifest = next(row for row in json.loads((ROOT / "analysis/pump_fun/program-manifest.json").read_text())["programs"]
                    if row["program"] == str(FEES))
    inventory = next(row for row in json.loads((ROOT / "analysis/pump_fun/elf-inventory.json").read_text())["programs"]
                     if row["name"] == "pump_fees")
    fixture = json.loads((ROOT / "analysis/pump_fun/amm-v2-trade-fixture.json").read_text())
    quote = Pubkey.from_string(fixture["keys"]["quote_mint"])
    mint_capture = fixture["accounts"]["quote_mint"]
    quote_template_capture = fixture["accounts"]["pool_quote_token_account"]
    idl = json.loads((ROOT / "third_party/pump-public-docs/idl/pump_fees.json").read_text())
    instruction = next(ix for ix in idl["instructions"] if ix["name"] == "withdraw")
    referral = Pubkey.find_program_address(
        [b"referral-vault", bytes(USER.pubkey())], FEES)[0]
    vault_ata = Pubkey.find_program_address(
        [bytes(referral), bytes(TOKEN), bytes(quote)], ATA)[0]
    user_ata = Pubkey.find_program_address(
        [bytes(USER.pubkey()), bytes(TOKEN), bytes(quote)], ATA)[0]
    outsider_ata = Pubkey.find_program_address(
        [bytes(OUTSIDER.pubkey()), bytes(TOKEN), bytes(quote)], ATA)[0]
    event = Pubkey.find_program_address([b"__event_authority"], FEES)[0]
    addresses = {"referral_vault": referral, "vault_ata": vault_ata,
                 "user_ata": user_ata, "outsider_ata": outsider_ata,
                 "quote_mint": quote}
    assert bytes(instruction["accounts"][1]["pda"]["seeds"][0]["value"]) == b"referral-vault"

    process = subprocess.Popen([str(ROOT / "tools/surfpool"), "start",
        "--offline", "--no-deploy", "--no-tui", "--no-studio",
        "--airdrop-amount", "0", "--port", str(PORT), "--ws-port",
        str(PORT + 1), "--db", ":memory:", "--log-level", "error"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(150):
            if process.poll() is not None:
                raise RuntimeError(process.stderr.read().decode()[-1000:])
            try:
                local.rpc("getHealth")
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(.1)
        else:
            raise TimeoutError("offline Surfpool did not start")
        local.set_account(USER.pubkey(), 10**12, b"", SYSTEM)
        local.set_account(OUTSIDER.pubkey(), 10**12, b"", SYSTEM)
        executable = (ROOT / manifest["path"]).read_bytes()
        assert sha(executable) == manifest["payload_sha256"]
        local.set_account(FEES, 10**10, executable[:inventory["elf_extent_bytes"]],
                          LOADER, True)
        mint_raw = base64.b64decode(mint_capture["data_base64"])
        assert sha(mint_raw) == mint_capture["data_sha256"]
        local.set_account(quote, mint_capture["lamports"], mint_raw,
                          mint_capture["owner"])
        local.set_account(referral, 1_000_000, b"", SYSTEM)
        template = bytearray(base64.b64decode(quote_template_capture["data_base64"]))
        assert sha(template) == quote_template_capture["data_sha256"]
        rent = struct.unpack_from("<Q", template, 113)[0]
        vault = bytearray(template)
        vault[32:64] = bytes(referral)
        struct.pack_into("<Q", vault, 64, INITIAL_VAULT_RAW)
        user = bytearray(template)
        user[32:64] = bytes(USER.pubkey())
        struct.pack_into("<Q", user, 64, 0)
        outsider = bytearray(template)
        outsider[32:64] = bytes(OUTSIDER.pubkey())
        struct.pack_into("<Q", outsider, 64, 0)
        local.set_account(vault_ata, rent + INITIAL_VAULT_RAW, vault, TOKEN)
        local.set_account(user_ata, rent, user, TOKEN)
        local.set_account(outsider_ata, rent, outsider, TOKEN)
        names = {"user": USER.pubkey(), "referral_vault": referral,
                 "quote_mint": quote, "vault_ata": vault_ata,
                 "user_ata": user_ata, "token_program": TOKEN,
                 "system_program": SYSTEM,
                 "event_authority": event, "program": FEES}
        metas = [AccountMeta(names[a["name"]], bool(a.get("signer")),
                             bool(a.get("writable"))) for a in instruction["accounts"]]
        unsigned = [AccountMeta(OUTSIDER.pubkey() if a.pubkey == USER.pubkey()
                    else a.pubkey, a.is_signer, a.is_writable) for a in metas]
        missing_signature = [AccountMeta(a.pubkey, False if a.pubkey == USER.pubkey()
                             else a.is_signer, a.is_writable) for a in metas]
        redirected = [AccountMeta(outsider_ata if a.pubkey == user_ata
                      else a.pubkey, a.is_signer, a.is_writable) for a in metas]
        cases = [send("unsigned_user_rejected", Instruction(FEES,
            bytes(instruction["discriminator"]), missing_signature), OUTSIDER,
            addresses, False),
            send("wrong_user_rejected", Instruction(FEES,
            bytes(instruction["discriminator"]), unsigned), OUTSIDER,
            addresses, False),
            send("redirected_recipient_rejected", Instruction(FEES,
                bytes(instruction["discriminator"]), redirected), USER,
                addresses, False),
            send("withdraw", Instruction(FEES,
                bytes(instruction["discriminator"]), metas), USER,
                addresses, True)]
        before, after = cases[-1]["before"], cases[-1]["after"]
        assert before["vault_ata"]["token_amount"] + before["user_ata"]["token_amount"] == \
               after["vault_ata"]["token_amount"] + after["user_ata"]["token_amount"]
        assert after["user_ata"]["token_amount"] - before["user_ata"]["token_amount"] == \
               INITIAL_VAULT_RAW
        OUT.write_text(json.dumps({"environment": "offline Surfpool :memory: loopback",
            "program": str(FEES), "payload_sha256": manifest["payload_sha256"],
            "loaded_elf_extent": inventory["elf_extent_bytes"],
            "source_mint_sha256": mint_capture["data_sha256"],
            "source_token_layout_sha256": quote_template_capture["data_sha256"],
            "synthetic_user": str(USER.pubkey()),
            "accounts": {name: str(address) for name, address in addresses.items()},
            "initial_vault_raw": INITIAL_VAULT_RAW,
            "cases": cases,
            "qualification": "Pinned current Pump Fees ELF and captured wrapped-SOL mint/token layout. Referral vault, its WSOL ATA, user ATA, funding and signer are synthetic disposable local accounts. Signed transactions are committed only in offline Surfpool; this does not establish live accrued fees, real user entitlement or full handler behavior. No public RPC or mainnet transaction."},
            indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT), "cases": len(cases),
            "paid_raw": after["user_ata"]["token_amount"] -
                        before["user_ata"]["token_amount"]}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
