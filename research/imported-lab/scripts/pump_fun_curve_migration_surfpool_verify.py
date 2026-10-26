"""Verify signed fresh Pump completion and PumpSwap migrate_v2 offline."""

import base64
import hashlib
import json
import struct
from pathlib import Path

from solders.pubkey import Pubkey
from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
COMPLETE = LANE / "curve-completion-signed-surfpool.json"
MIGRATE = LANE / "curve-migrate-v2-signed-surfpool.json"
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
TOKEN2022 = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
ATA = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw(row):
    value = base64.b64decode(row["data_base64"])
    assert sha(value) == row["data_sha256"]
    return value


def u64(data, at):
    return struct.unpack_from("<Q", data, at)[0]


def lamports(state):
    return sum(row["lamports"] if row else 0 for row in state.values())


def token_total(state):
    return sum(state[name]["token_amount"] if state[name] else 0 for name in
               ("curve_base", "user_base", "pool_authority_mint", "pool_base"))


def signature(row, expected_accounts=None):
    tx = Transaction.from_bytes(base64.b64decode(row["transaction_base64"]))
    assert all(tx.verify_with_results())
    assert str(tx.signatures[0]) == row["signature"]
    assert row["simulation_error"] == row["committed_error"]
    if expected_accounts is not None:
        assert len(tx.message.instructions[-1].accounts) == expected_accounts


def failed_rollback(row, code):
    assert row["committed_error"] == {"InstructionError": [1, {"Custom": code}]}
    for name in row["before"]:
        if name == "user":
            assert row["before"][name]["lamports"] - \
                   row["after"][name]["lamports"] == 5000
            assert row["before"][name]["data_sha256"] == \
                   row["after"][name]["data_sha256"]
        else:
            assert row["before"][name] == row["after"][name]


def main():
    completion = json.loads(COMPLETE.read_text())
    migration = json.loads(MIGRATE.read_text())
    trades = json.loads((LANE / "curve-fresh-trades-v3-signed-surfpool.json").read_text())
    manifest = {Path(row["path"]).stem: row for row in json.loads(
        (LANE / "program-manifest.json").read_text())["programs"]}
    provenance_path = LANE / "sdk-migration-account-provenance.json"
    provenance = json.loads(provenance_path.read_text())
    assert provenance["package"] == "@pump-fun/pump-sdk"
    assert provenance["version"] == "4.3.1"
    assert sha(provenance_path.read_bytes()) == migration["sdk_provenance_sha256"]
    assert migration["remaining_account_count"] == len(provenance["appended_remaining_accounts"]) == 2
    assert migration["fixed_idl_account_count"] == provenance["fixed_idl_account_count"] == 27
    assert completion["environment"] == migration["environment"] == \
           "offline Surfpool :memory: loopback"
    assert completion["program"] == trades["program"] == manifest["pump"]["program"]
    assert migration["pump_program_sha256"] == sha((ROOT / manifest["pump"]["path"]).read_bytes())
    assert migration["amm_program_sha256"] == sha((ROOT / manifest["pump_amm"]["path"]).read_bytes())
    assert completion["fresh_mint"] == migration["fresh_mint"] == trades["created_mint"]
    assert completion["fresh_curve"] == migration["fresh_curve"] == trades["created_curve"]
    assert completion["disposable_user"] == trades["disposable_user"]
    assert len(completion["steps"]) == 2
    completed, closed_reject = completion["steps"]
    assert completed["label"] == "complete_curve_buy_v3"
    assert closed_reject["label"] == "completed_curve_sell_rejected"
    signature(completed)
    signature(closed_reject)
    assert completed["committed_error"] is None
    assert completed["before"] == trades["steps"][-1]["after"]
    assert completion["remaining_real_token_reserves_before"] == \
           u64(raw(completed["before"]["curve"]), 24) == 793_099_500_000_000
    after_curve = raw(completed["after"]["curve"])
    assert after_curve[48] == 1 and u64(after_curve, 24) == 0
    assert completed["after"]["user_base"]["token_amount"] - \
           completed["before"]["user_base"]["token_amount"] == \
           completion["remaining_real_token_reserves_before"]
    assert completed["after"]["curve_base"]["token_amount"] == 206_900_000_000_000
    assert lamports(completed["before"]) - lamports(completed["after"]) == 5000
    assert closed_reject["before"] == completed["after"]
    failed_rollback(closed_reject, 6005)

    missing = migration["missing_boost"]
    executed = migration["migration"]
    assert missing["label"] == "migrate_v2_missing_boost_rollback"
    assert executed["label"] == "migrate_v2"
    signature(missing, 27)
    signature(executed, 29)
    assert migration["completion_signature"] == completed["signature"]
    for name in ("user", "mint", "curve", "curve_base", "user_base", "global"):
        assert missing["before"][name] == closed_reject["after"][name]
    failed_rollback(missing, 6027)
    assert any("NotEnoughRemainingAccounts" in line for line in missing["log_tail"])
    assert executed["before"] == missing["after"]
    assert executed["committed_error"] is None
    before, after = executed["before"], executed["after"]
    assert lamports(before) - lamports(after) == 5000
    assert token_total(before) == token_total(after) == 1_000_000_000_000_000
    assert before["pool"] is None and after["pool"] is not None
    assert after["pool"]["owner"] == manifest["pump_amm"]["program"]
    assert before["curve_base"]["token_amount"] == \
           after["pool_base"]["token_amount"] == 206_900_000_000_000
    assert after["curve_base"]["token_amount"] == 0
    curve_before, curve_after = raw(before["curve"]), raw(after["curve"])
    assert curve_before[48] == curve_after[48] == 1
    assert [u64(curve_after, at) for at in (8, 16, 24, 32)] == [0, 0, 0, 0]
    global_data = raw(before["global"])
    migration_fee = u64(global_data, 146)
    assert migration_fee == 15_000_001
    deposited_quote = after["pool_quote"]["token_amount"] + \
                      after["boost_vault"]["token_amount"]
    assert deposited_quote == u64(curve_before, 32) - migration_fee
    pool_data = raw(after["pool"])
    assert Pubkey.from_bytes(pool_data[43:75]) == \
           Pubkey.from_string(migration["fresh_mint"])
    assert Pubkey.from_bytes(pool_data[75:107]) == \
           Pubkey.from_string("So11111111111111111111111111111111111111112")
    pool = Pubkey.from_string(migration["pool"])
    mint = Pubkey.from_string(migration["fresh_mint"])
    quote = Pubkey.from_string("So11111111111111111111111111111111111111112")
    pool_base = Pubkey.find_program_address(
        [bytes(pool), bytes(TOKEN2022), bytes(mint)], ATA)[0]
    pool_quote = Pubkey.find_program_address(
        [bytes(pool), bytes(TOKEN), bytes(quote)], ATA)[0]
    assert Pubkey.from_bytes(pool_data[139:171]) == pool_base
    assert Pubkey.from_bytes(pool_data[171:203]) == pool_quote
    boost_authority = Pubkey.find_program_address(
        [b"boost_vault", bytes(pool)],
        Pubkey.from_string(manifest["pump_amm"]["program"]))[0]
    boost_vault = Pubkey.find_program_address(
        [bytes(boost_authority), bytes(TOKEN), bytes(quote)], ATA)[0]
    assert str(boost_authority) == migration["boost_authority"]
    assert str(boost_vault) == migration["boost_vault"]
    assert int.from_bytes(pool_data[245:261], "little", signed=True) == \
           after["boost_vault"]["token_amount"]
    assert after["pool_quote"]["token_amount"] + \
           int.from_bytes(pool_data[245:261], "little", signed=True) == deposited_quote
    assert u64(pool_data, 203) > 0
    print(json.dumps({"verified": True, "completed_buy_raw":
                      completion["remaining_real_token_reserves_before"],
                      "migration_fee_lamports": migration_fee,
                      "pool_base_raw": after["pool_base"]["token_amount"],
                      "pool_quote_raw": after["pool_quote"]["token_amount"],
                      "boost_quote_raw": after["boost_vault"]["token_amount"],
                      "completion_receipt": str(COMPLETE),
                      "migration_receipt": str(MIGRATE)}))


if __name__ == "__main__":
    main()
