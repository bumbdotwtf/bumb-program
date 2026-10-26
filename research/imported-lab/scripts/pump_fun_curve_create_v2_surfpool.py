"""Attempt fresh signed Pump create_v2 on a pinned offline Surfpool ledger."""

import base64
import hashlib
import json
import struct
import subprocess
import time
import urllib.error
from pathlib import Path

from solders.compute_budget import set_compute_unit_limit
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction

import pump_fun_admin_surfpool as local


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/pump_fun/curve-create-v2-signed-surfpool.json"
TRADES_OUT = ROOT / "analysis/pump_fun/curve-fresh-trades-v3-signed-surfpool.json"
COMPLETE_OUT = ROOT / "analysis/pump_fun/curve-completion-signed-surfpool.json"
MIGRATE_OUT = ROOT / "analysis/pump_fun/curve-migrate-v2-signed-surfpool.json"
POST_MIGRATE_OUT = ROOT / "analysis/pump_fun/post-migration-amm-v2-signed-surfpool.json"
PORT = 19891
PUMP = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
FEES = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
MAYHEM = Pubkey.from_string("MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e")
TOKEN2022 = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM = Pubkey.default()
LOADER = Pubkey.from_string("BPFLoader2111111111111111111111111111111111")
USER = Keypair.from_seed(bytes([231]) * 32)
MINT = Keypair.from_seed(bytes([232]) * 32)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get(address):
    value = local.rpc("getAccountInfo", [str(address), {"encoding": "base64"}])["value"]
    if value is None:
        return None
    return {"lamports": value["lamports"], "owner": value["owner"],
            "data": base64.b64decode(value["data"][0])}


def encode_string(value):
    raw = value.encode()
    return struct.pack("<I", len(raw)) + raw


def snapshot(addresses):
    rows = {}
    for name, address in addresses.items():
        item = get(address)
        if item is None:
            rows[name] = None
            continue
        row = {"lamports": item["lamports"], "owner": item["owner"],
               "data_sha256": sha(item["data"]),
               "data_base64": base64.b64encode(item["data"]).decode()}
        if item["owner"] in (str(TOKEN), str(TOKEN2022)) and len(item["data"]) in (165, 170):
            row["token_amount"] = struct.unpack_from("<Q", item["data"], 64)[0]
        rows[name] = row
    return rows


def submit(label, instructions, addresses, success):
    blockhash = Hash.from_string(local.rpc("getLatestBlockhash")["value"]["blockhash"])
    tx = Transaction.new_signed_with_payer(instructions, USER.pubkey(), [USER], blockhash)
    assert all(tx.verify_with_results())
    encoded = base64.b64encode(bytes(tx)).decode()
    before = snapshot(addresses)
    sim = local.rpc("simulateTransaction", [encoded,
        {"encoding": "base64", "sigVerify": True}])["value"]
    assert (sim["err"] is None) == success, (
        label, sim["err"], (sim.get("logs") or [])[-25:])
    signature = local.rpc("sendTransaction", [encoded,
        {"encoding": "base64", "skipPreflight": not success}])
    status = None
    for _ in range(100):
        status = local.rpc("getSignatureStatuses", [[signature]])["value"][0]
        if status is not None:
            break
        time.sleep(.05)
    assert status is not None and status["err"] == sim["err"]
    after = snapshot(addresses)
    if not success:
        for name in addresses:
            if name == "user":
                assert before[name]["data_sha256"] == after[name]["data_sha256"]
                assert before[name]["lamports"] - after[name]["lamports"] == 5000
            else:
                assert before[name] == after[name], (label, name)
    return {"label": label, "signature": signature,
            "transaction_base64": encoded, "simulation_error": sim["err"],
            "committed_error": status["err"],
            "units_consumed": sim.get("unitsConsumed"),
            "before": before, "after": after,
            "log_tail": (sim.get("logs") or [])[-20:]}


def main():
    local.PORT = PORT
    local.RPC = f"http://127.0.0.1:{PORT}"
    manifest = next(x for x in json.loads((ROOT / "analysis/pump_fun/program-manifest.json").read_text())["programs"]
                    if x["program"] == str(PUMP))
    inventory = next(x for x in json.loads((ROOT / "analysis/pump_fun/elf-inventory.json").read_text())["programs"]
                     if x["name"] == "pump")
    global_capture = next(x for x in json.loads((ROOT / "analysis/pump_fun/config-snapshot.json").read_text())["accounts"]
                          if x["program_name"] == "pump")
    idl = json.loads((ROOT / "third_party/pump-public-docs/idl/pump.json").read_text())
    selected = next(ix for ix in idl["instructions"] if ix["name"] == "create_v2")
    mint_authority = Pubkey.find_program_address([b"mint-authority"], PUMP)[0]
    curve = Pubkey.find_program_address([b"bonding-curve", bytes(MINT.pubkey())], PUMP)[0]
    curve_ata = Pubkey.find_program_address(
        [bytes(curve), bytes(TOKEN2022), bytes(MINT.pubkey())], ATA)[0]
    global_params = Pubkey.find_program_address([b"global-params"], MAYHEM)[0]
    sol_vault = Pubkey.find_program_address([b"sol-vault"], MAYHEM)[0]
    mayhem_state = Pubkey.find_program_address(
        [b"mayhem-state", bytes(MINT.pubkey())], MAYHEM)[0]
    mayhem_token_vault = Pubkey.find_program_address(
        [bytes(sol_vault), bytes(TOKEN2022), bytes(MINT.pubkey())], ATA)[0]
    event = Pubkey.find_program_address([b"__event_authority"], PUMP)[0]
    addresses = {"mint": MINT.pubkey(), "mint_authority": mint_authority,
        "bonding_curve": curve, "associated_bonding_curve": curve_ata,
        "global": Pubkey.from_string(global_capture["address"]),
        "user": USER.pubkey(), "system_program": SYSTEM,
        "token_program": TOKEN2022, "associated_token_program": ATA,
        "mayhem_program_id": MAYHEM, "global_params": global_params,
        "sol_vault": sol_vault, "mayhem_state": mayhem_state,
        "mayhem_token_vault": mayhem_token_vault,
        "event_authority": event, "program": PUMP}
    assert [x["name"] for x in selected["accounts"]] == list(addresses)
    metas = [AccountMeta(addresses[row["name"]], bool(row.get("signer")),
                         bool(row.get("writable"))) for row in selected["accounts"]]
    data = bytes(selected["discriminator"]) + \
           encode_string("Local Pump Test") + encode_string("LPT") + \
           encode_string("https://example.invalid/local-pump") + \
           bytes(USER.pubkey()) + bytes([0])

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
        elf = (ROOT / manifest["path"]).read_bytes()
        assert sha(elf) == manifest["payload_sha256"]
        local.set_account(PUMP, 10**10, elf[:inventory["elf_extent_bytes"]],
                          LOADER, True)
        global_data = base64.b64decode(global_capture["data_base64"])
        assert sha(global_data) == global_capture["data_sha256"]
        local.set_account(addresses["global"], global_capture["lamports"],
                          global_data, PUMP)
        assert get(MINT.pubkey()) is None and get(curve) is None
        blockhash = Hash.from_string(local.rpc("getLatestBlockhash")["value"]["blockhash"])
        tx = Transaction.new_signed_with_payer(
            [set_compute_unit_limit(1_400_000), Instruction(PUMP, data, metas)],
            USER.pubkey(), [USER, MINT], blockhash)
        assert all(tx.verify_with_results())
        encoded = base64.b64encode(bytes(tx)).decode()
        simulation = local.rpc("simulateTransaction", [encoded,
            {"encoding": "base64", "sigVerify": True}])["value"]
        if simulation["err"] is not None:
            print(json.dumps({"simulation_error": simulation["err"],
                "log_tail": (simulation.get("logs") or [])[-30:]}, indent=2))
            raise AssertionError("fresh create_v2 did not simulate successfully")
        signature = local.rpc("sendTransaction", [encoded,
            {"encoding": "base64"}])
        status = None
        for _ in range(100):
            status = local.rpc("getSignatureStatuses", [[signature]])["value"][0]
            if status is not None:
                break
            time.sleep(.05)
        assert status is not None and status["err"] is None
        accounts = {}
        for name in ("mint", "bonding_curve", "associated_bonding_curve", "global"):
            row = get(addresses[name])
            assert row is not None
            accounts[name] = {"address": str(addresses[name]),
                "lamports": row["lamports"], "owner": row["owner"],
                "data_sha256": sha(row["data"]),
                "data_base64": base64.b64encode(row["data"]).decode()}
        assert accounts["mint"]["owner"] == str(TOKEN2022)
        assert accounts["bonding_curve"]["owner"] == str(PUMP)
        assert accounts["associated_bonding_curve"]["owner"] == str(TOKEN2022)
        assert accounts["global"]["data_sha256"] == global_capture["data_sha256"]
        OUT.write_text(json.dumps({"environment": "offline Surfpool :memory: loopback",
            "program": str(PUMP), "payload_sha256": manifest["payload_sha256"],
            "loaded_elf_extent": inventory["elf_extent_bytes"],
            "global_capture_sha256": global_capture["data_sha256"],
            "disposable_user": str(USER.pubkey()), "disposable_mint": str(MINT.pubkey()),
            "instruction_data_hex": data.hex(), "transaction_base64": encoded,
            "signature": signature, "signature_verified": True,
            "simulation_error": simulation["err"], "committed_error": status["err"],
            "units_consumed": simulation.get("unitsConsumed"),
            "accounts": accounts,
            "qualification": "Fresh mint/curve/ATA created by pinned current Pump ELF with disposable local keys and copied captured Global only on offline Surfpool. Mayhem mode is false; optional quote accounts are omitted for a SOL-paired coin. No public RPC or live transaction was used for this execution. Handler behavior beyond this one local creation remains open."},
            indent=2) + "\n")

        fee_snapshot = json.loads((ROOT / "analysis/pump_fun/curve-fee-config-snapshot.json").read_text())
        assert fee_snapshot["global_data_sha256"] == global_capture["data_sha256"]
        fee_config = fee_snapshot["fee_config"]
        fee_bytes = base64.b64decode(fee_config["data_base64"])
        assert sha(fee_bytes) == fee_config["data_sha256"]
        fee_manifest = next(x for x in json.loads((ROOT / "analysis/pump_fun/program-manifest.json").read_text())["programs"]
                            if x["program"] == str(FEES))
        fee_inventory = next(x for x in json.loads((ROOT / "analysis/pump_fun/elf-inventory.json").read_text())["programs"]
                             if x["name"] == "pump_fees")
        fee_elf = (ROOT / fee_manifest["path"]).read_bytes()
        assert sha(fee_elf) == fee_manifest["payload_sha256"]
        local.set_account(FEES, 10**10, fee_elf[:fee_inventory["elf_extent_bytes"]],
                          LOADER, True)
        local.set_account(Pubkey.from_string(fee_config["address"]),
                          fee_config["lamports"], fee_bytes, FEES)
        amm_fixture = json.loads((ROOT / "analysis/pump_fun/amm-v2-trade-fixture.json").read_text())
        quote_mint = Pubkey.from_string(amm_fixture["keys"]["quote_mint"])
        quote_capture = amm_fixture["accounts"]["quote_mint"]
        quote_data = base64.b64decode(quote_capture["data_base64"])
        assert sha(quote_data) == quote_capture["data_sha256"]
        local.set_account(quote_mint, quote_capture["lamports"], quote_data,
                          quote_capture["owner"])
        buyback_capture = fee_snapshot["buyback_wallet"]
        buyback_data = base64.b64decode(buyback_capture["data_base64"])
        assert sha(buyback_data) == buyback_capture["data_sha256"]
        buyback = Pubkey.from_string(buyback_capture["address"])
        local.set_account(buyback, buyback_capture["lamports"],
                          buyback_data, buyback_capture["owner"])
        user_base = Pubkey.find_program_address(
            [bytes(USER.pubkey()), bytes(TOKEN2022), bytes(MINT.pubkey())], ATA)[0]
        curve_quote = Pubkey.find_program_address(
            [bytes(curve), bytes(TOKEN), bytes(quote_mint)], ATA)[0]
        user_quote = Pubkey.find_program_address(
            [bytes(USER.pubkey()), bytes(TOKEN), bytes(quote_mint)], ATA)[0]
        volume = Pubkey.find_program_address(
            [b"user_volume_accumulator", bytes(USER.pubkey())], PUMP)[0]
        watch = {"user": USER.pubkey(), "mint": MINT.pubkey(),
                 "quote_mint": quote_mint, "curve": curve,
                 "curve_base": curve_ata, "user_base": user_base,
                 "buyback": buyback, "volume": volume,
                 "global": addresses["global"],
                 "fee_config": Pubkey.from_string(fee_config["address"])}
        create_ata = Instruction(ATA, b"\x01", [
            AccountMeta(USER.pubkey(), True, True),
            AccountMeta(user_base, False, True),
            AccountMeta(USER.pubkey(), False, False),
            AccountMeta(MINT.pubkey(), False, False),
            AccountMeta(SYSTEM, False, False),
            AccountMeta(TOKEN2022, False, False)])
        steps = [submit("create_user_base_ata", [create_ata], watch, True)]
        buy = next(ix for ix in idl["instructions"] if ix["name"] == "buy_v3")
        buy_keys = {"global": addresses["global"], "base_mint": MINT.pubkey(),
            "quote_mint": quote_mint, "base_token_program": TOKEN2022,
            "quote_token_program": TOKEN, "bonding_curve": curve,
            "associated_base_bonding_curve": curve_ata,
            "associated_quote_bonding_curve": curve_quote,
            "user": USER.pubkey(), "associated_base_user": user_base,
            "associated_quote_user": user_quote,
            "user_volume_accumulator": volume,
            "fee_config": Pubkey.from_string(fee_config["address"]),
            "buyback_fee_recipient": buyback, "system_program": SYSTEM,
            "event_authority": event, "program": PUMP}
        buy_metas = [AccountMeta(buy_keys[a["name"]], bool(a.get("signer")),
                                 bool(a.get("writable"))) for a in buy["accounts"]]
        amount, max_cost = 1_000_000_000, 1_000_000_000
        steps.append(submit("buy_v3_tight_max_rollback", [
            set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(buy["discriminator"]) + struct.pack("<QQ", amount, 1),
                        buy_metas)], watch, False))
        steps.append(submit("buy_v3", [set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(buy["discriminator"]) +
                        struct.pack("<QQ", amount, max_cost), buy_metas)],
            watch, True))
        traded = steps[-1]
        assert traded["after"]["user_base"]["token_amount"] - \
               traded["before"]["user_base"]["token_amount"] == amount
        assert traded["before"]["curve_base"]["token_amount"] - \
               traded["after"]["curve_base"]["token_amount"] == amount
        assert traded["before"]["curve_base"]["token_amount"] + \
               traded["before"]["user_base"]["token_amount"] == \
               traded["after"]["curve_base"]["token_amount"] + \
               traded["after"]["user_base"]["token_amount"]
        assert traded["after"]["volume"] is not None
        sell = next(ix for ix in idl["instructions"] if ix["name"] == "sell_v3")
        assert [a["name"] for a in sell["accounts"]] == \
               [a["name"] for a in buy["accounts"]]
        sell_amount = 500_000_000
        steps.append(submit("sell_v3_high_min_rollback", [
            set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(sell["discriminator"]) +
                        struct.pack("<QQ", sell_amount, 1_000_000_000),
                        buy_metas)], watch, False))
        steps.append(submit("sell_v3", [set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(sell["discriminator"]) +
                        struct.pack("<QQ", sell_amount, 1), buy_metas)],
            watch, True))
        sold = steps[-1]
        assert sold["before"]["user_base"]["token_amount"] - \
               sold["after"]["user_base"]["token_amount"] == sell_amount
        assert sold["after"]["curve_base"]["token_amount"] - \
               sold["before"]["curve_base"]["token_amount"] == sell_amount
        TRADES_OUT.write_text(json.dumps({"environment": "offline Surfpool :memory: loopback",
            "program": str(PUMP), "payload_sha256": manifest["payload_sha256"],
            "fee_program_sha256": fee_manifest["payload_sha256"],
            "global_capture_sha256": global_capture["data_sha256"],
            "fee_config_capture_sha256": fee_config["data_sha256"],
            "quote_mint_capture_sha256": quote_capture["data_sha256"],
            "buyback_capture_sha256": buyback_capture["data_sha256"],
            "create_signature": signature,
            "created_mint": str(MINT.pubkey()), "created_curve": str(curve),
            "disposable_user": str(USER.pubkey()),
            "base_amount_out": amount, "max_sol_cost": max_cost,
            "base_amount_sold": sell_amount,
            "accounts": {name: str(key) for name, key in watch.items()},
            "steps": steps,
            "qualification": "Pinned current Pump and Pump Fees ELFs, fresh Pump-created Token-2022 mint/curve and copied finalized Global/FeeConfig/WSOL mint. User, mint and all SOL funding are disposable local keys. Signed ATA creation and buy_v3/sell_v3 trades with tight-limit rejections commit only in offline Surfpool. This is one SOL-paired non-Mayhem state, not live trade safety or full handler reversal; no public RPC or mainnet transaction."},
            indent=2) + "\n")
        remaining = struct.unpack_from("<Q", get(curve)["data"], 24)[0]
        assert remaining > 0
        completion = submit("complete_curve_buy_v3", [
            set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(buy["discriminator"]) +
                        struct.pack("<QQ", remaining, 200_000_000_000),
                        buy_metas)], watch, True)
        after_complete = base64.b64decode(completion["after"]["curve"]["data_base64"])
        assert after_complete[48] == 1
        assert struct.unpack_from("<Q", after_complete, 24)[0] == 0
        assert completion["after"]["user_base"]["token_amount"] - \
               completion["before"]["user_base"]["token_amount"] == remaining
        completed_reject = submit("completed_curve_sell_rejected", [
            set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(sell["discriminator"]) +
                        struct.pack("<QQ", 1, 1), buy_metas)], watch, False)
        COMPLETE_OUT.write_text(json.dumps({
            "environment": "offline Surfpool :memory: loopback",
            "program": str(PUMP), "payload_sha256": manifest["payload_sha256"],
            "fresh_mint": str(MINT.pubkey()), "fresh_curve": str(curve),
            "disposable_user": str(USER.pubkey()),
            "remaining_real_token_reserves_before": remaining,
            "steps": [completion, completed_reject],
            "qualification": "Completes the same fresh, regular SOL-paired Pump curve after signed local buy_v3/sell_v3. The exact remaining real-token reserve is bought with a disposable local payer; a subsequent sell is rejected atomically. This is an offline executable bound, not a live coin, migration proof, or full behavior reversal."},
            indent=2) + "\n")

        amm_program = Pubkey.from_string(
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
        amm_manifest = next(x for x in json.loads((ROOT / "analysis/pump_fun/program-manifest.json").read_text())["programs"]
                            if x["program"] == str(amm_program))
        amm_inventory = next(x for x in json.loads((ROOT / "analysis/pump_fun/elf-inventory.json").read_text())["programs"]
                             if x["name"] == "pump_amm")
        amm_elf = (ROOT / amm_manifest["path"]).read_bytes()
        assert sha(amm_elf) == amm_manifest["payload_sha256"]
        local.set_account(amm_program, 10**10,
                          amm_elf[:amm_inventory["elf_extent_bytes"]],
                          LOADER, True)
        amm_capture = next(x for x in json.loads((ROOT / "analysis/pump_fun/config-snapshot.json").read_text())["accounts"]
                           if x["program_name"] == "pump_amm")
        amm_config = Pubkey.from_string(amm_capture["address"])
        amm_data = base64.b64decode(amm_capture["data_base64"])
        assert sha(amm_data) == amm_capture["data_sha256"]
        local.set_account(amm_config, amm_capture["lamports"], amm_data,
                          amm_program)
        withdraw_authority = Pubkey.from_bytes(global_data[113:145])
        local.set_account(withdraw_authority, 0, b"", SYSTEM)
        pool_authority = Pubkey.find_program_address(
            [b"pool-authority", bytes(MINT.pubkey())], PUMP)[0]
        pool = Pubkey.find_program_address([b"pool", bytes(2),
            bytes(pool_authority), bytes(MINT.pubkey()), bytes(quote_mint)],
            amm_program)[0]
        lp_mint = Pubkey.find_program_address(
            [b"pool_lp_mint", bytes(pool)], amm_program)[0]
        def ata_for(owner, mint, token_program):
            return Pubkey.find_program_address(
                [bytes(owner), bytes(token_program), bytes(mint)], ATA)[0]
        pool_authority_mint = ata_for(pool_authority, MINT.pubkey(), TOKEN2022)
        pool_authority_quote = ata_for(pool_authority, quote_mint, TOKEN)
        pool_base = ata_for(pool, MINT.pubkey(), TOKEN2022)
        pool_quote = ata_for(pool, quote_mint, TOKEN)
        user_lp = ata_for(pool_authority, lp_mint, TOKEN2022)
        boost_authority = Pubkey.find_program_address(
            [b"boost_vault", bytes(pool)], amm_program)[0]
        boost_vault = ata_for(boost_authority, quote_mint, TOKEN)
        amm_event = Pubkey.find_program_address([b"__event_authority"],
                                                 amm_program)[0]
        rent_sysvar = Pubkey.from_string(
            "SysvarRent111111111111111111111111111111111")
        migrate = next(ix for ix in idl["instructions"]
                       if ix["name"] == "migrate_v2")
        migrate_keys = {"global": addresses["global"],
            "withdraw_authority": withdraw_authority,
            "base_mint": MINT.pubkey(), "quote_mint": quote_mint,
            "bonding_curve": curve,
            "associated_base_bonding_curve": curve_ata,
            "associated_quote_bonding_curve": curve_quote,
            "user": USER.pubkey(), "system_program": SYSTEM,
            "pump_amm": amm_program, "pool": pool,
            "pool_authority": pool_authority,
            "pool_authority_mint_account": pool_authority_mint,
            "pool_authority_quote_account": pool_authority_quote,
            "amm_global_config": amm_config, "lp_mint": lp_mint,
            "user_pool_token_account": user_lp,
            "pool_base_token_account": pool_base,
            "pool_quote_token_account": pool_quote,
            "base_token_program": TOKEN2022,
            "quote_token_program": TOKEN,
            "token_2022_program": TOKEN2022,
            "associated_token_program": ATA,
            "pump_amm_event_authority": amm_event,
            "rent": rent_sysvar, "event_authority": event,
            "program": PUMP}
        assert [a["name"] for a in migrate["accounts"]] == list(migrate_keys)
        migrate_metas = [AccountMeta(migrate_keys[a["name"]],
                                     bool(a.get("signer")),
                                     bool(a.get("writable")))
                         for a in migrate["accounts"]]
        # Official @pump-fun/pump-sdk 4.3.1 appends two accounts absent from
        # the 27 fixed IDL entries. They are required by the current binary.
        migrate_metas[3] = AccountMeta(quote_mint, False, True)
        migrate_metas.extend([
            AccountMeta(boost_authority, False, False),
            AccountMeta(boost_vault, False, True)])
        migration_watch = {"user": USER.pubkey(), "mint": MINT.pubkey(),
            "curve": curve, "curve_base": curve_ata,
            "user_base": user_base, "withdraw_authority": withdraw_authority,
            "pool": pool, "pool_authority": pool_authority,
            "boost_authority": boost_authority, "boost_vault": boost_vault,
            "pool_authority_mint": pool_authority_mint,
            "pool_authority_quote": pool_authority_quote,
            "pool_base": pool_base, "pool_quote": pool_quote,
            "lp_mint": lp_mint, "user_lp": user_lp,
            "global": addresses["global"], "amm_global_config": amm_config}
        assert get(pool) is None
        missing_boost = submit("migrate_v2_missing_boost_rollback", [
            set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(migrate["discriminator"]),
                        migrate_metas[:-2])], migration_watch, False)
        assert missing_boost["committed_error"] == {
            "InstructionError": [1, {"Custom": 6027}]}
        migrated = submit("migrate_v2", [set_compute_unit_limit(1_400_000),
            Instruction(PUMP, bytes(migrate["discriminator"]), migrate_metas)],
            migration_watch, True)
        assert migrated["after"]["pool"] is not None
        assert migrated["after"]["pool"]["owner"] == str(amm_program)
        MIGRATE_OUT.write_text(json.dumps({
            "environment": "offline Surfpool :memory: loopback",
            "pump_program_sha256": manifest["payload_sha256"],
            "amm_program_sha256": amm_manifest["payload_sha256"],
            "fresh_mint": str(MINT.pubkey()), "fresh_curve": str(curve),
            "pool": str(pool), "pool_authority": str(pool_authority),
            "boost_authority": str(boost_authority),
            "boost_vault": str(boost_vault),
            "remaining_accounts_source": "@pump-fun/pump-sdk@4.3.1 migrateV2Instruction",
            "sdk_provenance_sha256": sha((ROOT / "analysis/pump_fun/sdk-migration-account-provenance.json").read_bytes()),
            "fixed_idl_account_count": len(migrate["accounts"]),
            "remaining_account_count": 2,
            "completion_signature": completion["signature"],
            "missing_boost": missing_boost, "migration": migrated,
            "qualification": "Current Pump and Pump AMM ELFs, fresh locally completed SOL-paired non-Mayhem curve and copied finalized configs. All signers and funding are disposable local. Migration is a signed offline Surfpool commit, not a live fund movement, exact source build or full handler reversal."},
            indent=2) + "\n")

        # Trade against the exact pool produced above, with a signed local
        # wrapped-SOL funding transaction rather than a synthetic token edit.
        amm_idl = json.loads((ROOT / "third_party/pump-public-docs/idl/pump_amm.json").read_text())
        amm_buy = next(ix for ix in amm_idl["instructions"] if ix["name"] == "buy_v2")
        amm_sell = next(ix for ix in amm_idl["instructions"] if ix["name"] == "sell_v2")
        amm_fee_config_capture = amm_fixture["accounts"]["fee_config"]
        amm_fee_config = Pubkey.from_string(amm_fee_config_capture["address"])
        amm_fee_config_data = base64.b64decode(amm_fee_config_capture["data_base64"])
        assert sha(amm_fee_config_data) == amm_fee_config_capture["data_sha256"]
        local.set_account(amm_fee_config, amm_fee_config_capture["lamports"],
                          amm_fee_config_data, FEES)
        amm_buyback_capture = amm_fixture["accounts"]["buyback_fee_recipient"]
        amm_buyback = Pubkey.from_string(amm_buyback_capture["address"])
        amm_buyback_data = base64.b64decode(amm_buyback_capture["data_base64"])
        assert sha(amm_buyback_data) == amm_buyback_capture["data_sha256"]
        local.set_account(amm_buyback, amm_buyback_capture["lamports"],
                          amm_buyback_data, amm_buyback_capture["owner"])
        amm_volume = Pubkey.find_program_address(
            [b"user_volume_accumulator", bytes(USER.pubkey())], amm_program)[0]
        amm_watch = {"user": USER.pubkey(), "pool": pool,
            "user_base": user_base, "user_quote": user_quote,
            "pool_base": pool_base, "pool_quote": pool_quote,
            "boost_vault": boost_vault, "buyback": amm_buyback,
            "volume": amm_volume, "global_config": amm_config,
            "fee_config": amm_fee_config}
        fund_quote = submit("create_and_fund_user_wsol", [
            Instruction(ATA, b"\x01", [
                AccountMeta(USER.pubkey(), True, True),
                AccountMeta(user_quote, False, True),
                AccountMeta(USER.pubkey(), False, False),
                AccountMeta(quote_mint, False, False),
                AccountMeta(SYSTEM, False, False),
                AccountMeta(TOKEN, False, False)]),
            Instruction(SYSTEM, b"\x02\x00\x00\x00" + struct.pack("<Q", 1_000_000_000), [
                AccountMeta(USER.pubkey(), True, True),
                AccountMeta(user_quote, False, True)]),
            Instruction(TOKEN, bytes([17]), [AccountMeta(user_quote, False, True)])
            ], amm_watch, True)
        assert fund_quote["after"]["user_quote"]["token_amount"] == 1_000_000_000
        amm_keys = {"pool": pool, "user": USER.pubkey(),
            "global_config": amm_config, "base_mint": MINT.pubkey(),
            "quote_mint": quote_mint, "user_base_token_account": user_base,
            "user_quote_token_account": user_quote,
            "pool_base_token_account": pool_base,
            "pool_quote_token_account": pool_quote,
            "base_token_program": TOKEN2022, "quote_token_program": TOKEN,
            "system_program": SYSTEM, "user_volume_accumulator": amm_volume,
            "fee_config": amm_fee_config,
            "buyback_fee_recipient": amm_buyback,
            "event_authority": amm_event, "program": amm_program}
        assert [a["name"] for a in amm_buy["accounts"]] == list(amm_keys)
        assert [a["name"] for a in amm_sell["accounts"]] == list(amm_keys)
        amm_metas = [AccountMeta(amm_keys[a["name"]], bool(a.get("signer")),
                                 bool(a.get("writable"))) for a in amm_buy["accounts"]]
        trade_amount = 1_000_000_000
        amm_buy_ix = Instruction(amm_program, bytes(amm_buy["discriminator"]) +
            struct.pack("<QQ", trade_amount, 1_000_000_000), amm_metas)
        tight_buy = submit("fresh_pool_buy_v2_tight_max_rollback", [
            set_compute_unit_limit(1_400_000),
            Instruction(amm_program, bytes(amm_buy["discriminator"]) +
                struct.pack("<QQ", trade_amount, 1), amm_metas)],
            amm_watch, False)
        bought = submit("fresh_pool_buy_v2", [
            set_compute_unit_limit(1_400_000), amm_buy_ix], amm_watch, True)
        assert bought["after"]["user_base"]["token_amount"] - \
               bought["before"]["user_base"]["token_amount"] == trade_amount
        sell_amount = 500_000_000
        high_min_sell = submit("fresh_pool_sell_v2_high_min_rollback", [
            set_compute_unit_limit(1_400_000),
            Instruction(amm_program, bytes(amm_sell["discriminator"]) +
                struct.pack("<QQ", sell_amount, 1_000_000_000), amm_metas)],
            amm_watch, False)
        sold_pool = submit("fresh_pool_sell_v2", [
            set_compute_unit_limit(1_400_000),
            Instruction(amm_program, bytes(amm_sell["discriminator"]) +
                struct.pack("<QQ", sell_amount, 1), amm_metas)],
            amm_watch, True)
        assert sold_pool["before"]["user_base"]["token_amount"] - \
               sold_pool["after"]["user_base"]["token_amount"] == sell_amount
        POST_MIGRATE_OUT.write_text(json.dumps({
            "environment": "offline Surfpool :memory: loopback",
            "amm_program": str(amm_program),
            "amm_program_sha256": amm_manifest["payload_sha256"],
            "fresh_mint": str(MINT.pubkey()), "fresh_pool": str(pool),
            "migration_signature": migrated["signature"],
            "disposable_user": str(USER.pubkey()),
            "base_amount_bought": trade_amount,
            "base_amount_sold": sell_amount,
            "steps": [fund_quote, tight_buy, bought, high_min_sell, sold_pool],
            "qualification": "The same offline pool created by the pinned Pump migrate_v2 transaction. Wrapped-SOL user funding, AMM v2 buy and sell are signed local transactions. Tests one regular SOL-paired Token-2022 base pool and fee configuration, not other pool modes or live fund safety."},
            indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT), "mint": str(MINT.pubkey()),
                          "curve": str(curve), "units": simulation.get("unitsConsumed"),
                          "trade_receipt": str(TRADES_OUT), "base_received": amount,
                          "base_sold": sell_amount, "completion_receipt": str(COMPLETE_OUT),
                          "completed_tokens_bought": remaining,
                          "migration_receipt": str(MIGRATE_OUT),
                          "post_migration_trade_receipt": str(POST_MIGRATE_OUT)}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
