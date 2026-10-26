"""Signed, committed offline PumpSwap buy_v2 on a captured current pool.

The trader and its token accounts are disposable local constructions. Pinned
program/pool/vault/config bytes come from finalized read-only captures.
"""

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
OUT = ROOT / "analysis/pump_fun/amm-buy-v2-signed-surfpool.json"
PORT = 19851
AMM = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
FEES = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM = Pubkey.default()
LOADER = Pubkey.from_string("BPFLoader2111111111111111111111111111111111")
TRADER = Keypair.from_seed(bytes([211]) * 32)
OUTSIDER = Keypair.from_seed(bytes([212]) * 32)
BASE_OUT = 10_000_000_000
MAX_QUOTE_IN = 1_000_000_000
SELL_IN = 5_000_000_000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get(address):
    row = local.rpc("getAccountInfo", [str(address), {"encoding": "base64"}])["value"]
    if row is None:
        return None
    raw = base64.b64decode(row["data"][0])
    return {"lamports": row["lamports"], "owner": row["owner"],
            "data": raw}


def watched(addresses):
    result = {}
    for name, address in addresses.items():
        row = get(address)
        if row is None:
            result[name] = None
            continue
        item = {"lamports": row["lamports"], "owner": row["owner"],
                "data_sha256": sha(row["data"]),
                "data_base64": base64.b64encode(row["data"]).decode()}
        if row["owner"] == str(TOKEN) and len(row["data"]) == 165:
            item["token_amount"] = struct.unpack_from("<Q", row["data"], 64)[0]
        result[name] = item
    return result


def totals(state):
    return {"base": sum(state[name]["token_amount"] for name in
                        ("user_base", "pool_base")),
            "quote": sum(state[name]["token_amount"] for name in
                         ("user_quote", "pool_quote", "buyback_quote"))}


def send(label, instruction, payer, addresses, expect_success):
    blockhash = Hash.from_string(local.rpc("getLatestBlockhash")["value"]["blockhash"])
    tx = Transaction.new_signed_with_payer([instruction], payer.pubkey(),
                                            [payer], blockhash)
    assert all(tx.verify_with_results())
    encoded = base64.b64encode(bytes(tx)).decode()
    before = watched(addresses)
    payer_before = get(payer.pubkey())["lamports"]
    sim = local.rpc("simulateTransaction", [encoded,
        {"encoding": "base64", "sigVerify": True}])["value"]
    assert (sim["err"] is None) == expect_success, (
        label, sim["err"], (sim.get("logs") or [])[-25:])
    signature = local.rpc("sendTransaction", [encoded,
        {"encoding": "base64", "skipPreflight": not expect_success}])
    status = None
    for _ in range(100):
        status = local.rpc("getSignatureStatuses", [[signature]])["value"][0]
        if status is not None:
            break
        time.sleep(.05)
    assert status is not None and status["err"] == sim["err"]
    after = watched(addresses)
    if not expect_success:
        assert before == after, label
    return {"label": label, "signature": signature,
            "transaction_base64": encoded,
            "simulation_error": sim["err"], "committed_error": status["err"],
            "units_consumed": sim.get("unitsConsumed"),
            "payer_lamports_spent": payer_before - get(payer.pubkey())["lamports"],
            "before": before, "after": after,
            "log_tail": (sim.get("logs") or [])[-20:]}


def main():
    local.PORT = PORT
    local.RPC = f"http://127.0.0.1:{PORT}"
    fixture = json.loads((ROOT / "analysis/pump_fun/amm-v2-trade-fixture.json").read_text())
    config = next(row for row in json.loads((ROOT / "analysis/pump_fun/config-snapshot.json").read_text())["accounts"]
                  if row["program_name"] == "pump_amm")
    inventory = {row["name"]: row for row in json.loads((ROOT / "analysis/pump_fun/elf-inventory.json").read_text())["programs"]}
    manifest = {Path(row["path"]).stem: row for row in json.loads((ROOT / "analysis/pump_fun/program-manifest.json").read_text())["programs"]}
    idl = json.loads((ROOT / "third_party/pump-public-docs/idl/pump_amm.json").read_text())
    ix = next(row for row in idl["instructions"] if row["name"] == "buy_v2")
    sell_ix = next(row for row in idl["instructions"] if row["name"] == "sell_v2")
    assert [a["name"] for a in ix["accounts"]] == \
           [a["name"] for a in sell_ix["accounts"]]
    assert fixture["pool"] == fixture["accounts"]["pool"]["address"]
    keys = fixture["keys"]
    base_mint, quote_mint = (Pubkey.from_string(keys[name]) for name in
                             ("base_mint", "quote_mint"))
    user_base = Pubkey.find_program_address(
        [bytes(TRADER.pubkey()), bytes(TOKEN), bytes(base_mint)], ATA)[0]
    user_quote = Pubkey.find_program_address(
        [bytes(TRADER.pubkey()), bytes(TOKEN), bytes(quote_mint)], ATA)[0]
    volume = Pubkey.find_program_address(
        [b"user_volume_accumulator", bytes(TRADER.pubkey())], AMM)[0]
    event = Pubkey.find_program_address([b"__event_authority"], AMM)[0]
    addresses = {"pool": Pubkey.from_string(fixture["pool"]),
                 "user_base": user_base, "user_quote": user_quote,
                 "pool_base": Pubkey.from_string(keys["pool_base_token_account"]),
                 "pool_quote": Pubkey.from_string(keys["pool_quote_token_account"]),
                 "buyback_quote": Pubkey.from_string(fixture["accounts"]["buyback_fee_recipient"]["address"]),
                 "volume": volume,
                 "global_config": Pubkey.from_string(config["address"]),
                 "fee_config": Pubkey.from_string(keys["fee_config"])}
    assert bytes.fromhex(fixture["fee_config_seed_hex"][0]) == b"fee_config"

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
        local.set_account(TRADER.pubkey(), 10**12, b"", SYSTEM)
        local.set_account(OUTSIDER.pubkey(), 10**12, b"", SYSTEM)
        for name, program in (("pump_amm", AMM), ("pump_fees", FEES)):
            blob = (ROOT / manifest[name]["path"]).read_bytes()
            assert sha(blob) == manifest[name]["payload_sha256"]
            local.set_account(program, 10**10,
                blob[:inventory[name]["elf_extent_bytes"]], LOADER, True)
        for name, row in fixture["accounts"].items():
            raw = base64.b64decode(row["data_base64"])
            assert sha(raw) == row["data_sha256"]
            local.set_account(Pubkey.from_string(row["address"]), row["lamports"],
                              raw, row["owner"], row["executable"])
        config_data = base64.b64decode(config["data_base64"])
        assert sha(config_data) == config["data_sha256"]
        local.set_account(Pubkey.from_string(config["address"]), config["lamports"],
                          config_data, AMM)
        base_template = bytearray(base64.b64decode(
            fixture["accounts"]["pool_base_token_account"]["data_base64"]))
        quote_template = bytearray(base64.b64decode(
            fixture["accounts"]["pool_quote_token_account"]["data_base64"]))
        base_template[32:64] = bytes(TRADER.pubkey())
        quote_template[32:64] = bytes(TRADER.pubkey())
        struct.pack_into("<Q", base_template, 64, 0)
        struct.pack_into("<Q", quote_template, 64, 2_000_000_000)
        local.set_account(user_base, 2_039_280, base_template, TOKEN)
        native_rent = struct.unpack_from("<Q", quote_template, 113)[0]
        local.set_account(user_quote, native_rent + 2_000_000_000,
                          quote_template, TOKEN)
        assert get(volume) is None
        key_map = {"pool": addresses["pool"], "user": TRADER.pubkey(),
            "global_config": addresses["global_config"],
            "base_mint": base_mint, "quote_mint": quote_mint,
            "user_base_token_account": user_base,
            "user_quote_token_account": user_quote,
            "pool_base_token_account": addresses["pool_base"],
            "pool_quote_token_account": addresses["pool_quote"],
            "base_token_program": TOKEN, "quote_token_program": TOKEN,
            "system_program": SYSTEM,
            "user_volume_accumulator": volume,
            "fee_config": addresses["fee_config"],
            "buyback_fee_recipient": addresses["buyback_quote"],
            "event_authority": event, "program": AMM}
        metas = [AccountMeta(key_map[row["name"]], bool(row.get("signer")),
                             bool(row.get("writable"))) for row in ix["accounts"]]
        instruction_data = bytes(ix["discriminator"]) + struct.pack(
            "<QQ", BASE_OUT, MAX_QUOTE_IN)
        unsigned = [AccountMeta(row.pubkey, False if row.pubkey == TRADER.pubkey()
                    else row.is_signer, row.is_writable) for row in metas]
        cases = [send("unsigned_trader_rejected", Instruction(AMM,
            instruction_data, unsigned), OUTSIDER, addresses, False),
            send("max_quote_one_rollback", Instruction(AMM,
                bytes(ix["discriminator"]) + struct.pack("<QQ", BASE_OUT, 1),
                metas), TRADER, addresses, False),
            send("buy_v2", Instruction(AMM, instruction_data, metas),
                TRADER, addresses, True)]
        trade = cases[-1]
        assert totals(trade["before"]) == totals(trade["after"])
        assert trade["after"]["user_base"]["token_amount"] - \
               trade["before"]["user_base"]["token_amount"] == BASE_OUT
        assert trade["before"]["pool_base"]["token_amount"] - \
               trade["after"]["pool_base"]["token_amount"] == BASE_OUT
        assert trade["before"]["user_quote"]["token_amount"] > \
               trade["after"]["user_quote"]["token_amount"]
        sell_metas = [AccountMeta(key_map[row["name"]], bool(row.get("signer")),
                                  bool(row.get("writable")))
                      for row in sell_ix["accounts"]]
        cases.append(send("sell_v2_high_min_rollback", Instruction(AMM,
            bytes(sell_ix["discriminator"]) + struct.pack("<QQ", SELL_IN,
                                                          1_000_000_000),
            sell_metas), TRADER, addresses, False))
        cases.append(send("sell_v2", Instruction(AMM,
            bytes(sell_ix["discriminator"]) + struct.pack("<QQ", SELL_IN, 1),
            sell_metas), TRADER, addresses, True))
        sold = cases[-1]
        assert totals(sold["before"]) == totals(sold["after"])
        assert sold["before"]["user_base"]["token_amount"] - \
               sold["after"]["user_base"]["token_amount"] == SELL_IN
        assert sold["after"]["pool_base"]["token_amount"] - \
               sold["before"]["pool_base"]["token_amount"] == SELL_IN
        assert sold["after"]["user_quote"]["token_amount"] > \
               sold["before"]["user_quote"]["token_amount"]
        OUT.write_text(json.dumps({"environment": "offline Surfpool :memory: loopback",
            "program_hashes": {name: manifest[name]["payload_sha256"]
                               for name in ("pump_amm", "pump_fees")},
            "fixture_sha256": sha((ROOT / "analysis/pump_fun/amm-v2-trade-fixture.json").read_bytes()),
            "pool": fixture["pool"], "captured_pool_slot": fixture["accounts"]["pool"]["slot"],
            "disposable_trader": str(TRADER.pubkey()),
            "accounts": {name: str(address) for name, address in addresses.items()},
            "base_amount_out": BASE_OUT, "max_quote_amount_in": MAX_QUOTE_IN,
            "base_amount_sold": SELL_IN,
            "cases": cases,
            "qualification": "Current pinned Pump AMM and Pump Fees ELFs on a captured later mainnet pool/fee snapshot. User token accounts, WSOL funding and signer are synthetic; the full executables are loaded without trailing zero allocation padding. Five submitted transactions are signed and committed only to offline Surfpool. This bounded v2 buy/sell path does not establish archival pre-trade state, live user exposure, every fee route, or full handler reversal. No public RPC or live transaction."},
            indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT), "cases": len(cases),
            "user_base_received": trade["after"]["user_base"]["token_amount"],
            "quote_spent": trade["before"]["user_quote"]["token_amount"] -
                           trade["after"]["user_quote"]["token_amount"],
            "quote_received_on_sell": sold["after"]["user_quote"]["token_amount"] -
                                      sold["before"]["user_quote"]["token_amount"]}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
