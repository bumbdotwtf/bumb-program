"""Verify signed fresh Pump create_v2 and v3 round-trip receipts offline."""

import base64
import hashlib
import json
import struct
from pathlib import Path

from solders.pubkey import Pubkey
from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
CREATE = LANE / "curve-create-v2-signed-surfpool.json"
TRADES = LANE / "curve-fresh-trades-v3-signed-surfpool.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw(row):
    value = base64.b64decode(row["data_base64"])
    assert sha(value) == row["data_sha256"]
    return value


def u64(data, offset):
    return struct.unpack_from("<Q", data, offset)[0]


def lamport_total(state):
    return sum(state[name]["lamports"] if state[name] else 0 for name in
               ("user", "curve", "buyback", "volume", "user_base"))


def main():
    created = json.loads(CREATE.read_text())
    traded = json.loads(TRADES.read_text())
    manifests = {Path(row["path"]).stem: row for row in json.loads(
        (LANE / "program-manifest.json").read_text())["programs"]}
    configs = json.loads((LANE / "config-snapshot.json").read_text())
    global_capture = next(row for row in configs["accounts"]
                          if row["program_name"] == "pump")
    fee_capture = json.loads((LANE / "curve-fee-config-snapshot.json").read_text())
    amm_fixture = json.loads((LANE / "amm-v2-trade-fixture.json").read_text())
    assert created["environment"] == traded["environment"] == \
           "offline Surfpool :memory: loopback"
    assert created["program"] == traded["program"] == manifests["pump"]["program"]
    assert created["payload_sha256"] == traded["payload_sha256"] == \
           sha((ROOT / manifests["pump"]["path"]).read_bytes())
    assert traded["fee_program_sha256"] == sha((ROOT / manifests["pump_fees"]["path"]).read_bytes())
    assert created["global_capture_sha256"] == traded["global_capture_sha256"] == \
           global_capture["data_sha256"]
    assert traded["fee_config_capture_sha256"] == fee_capture["fee_config"]["data_sha256"]
    assert traded["quote_mint_capture_sha256"] == \
           amm_fixture["accounts"]["quote_mint"]["data_sha256"]
    assert traded["buyback_capture_sha256"] == fee_capture["buyback_wallet"]["data_sha256"]
    assert traded["create_signature"] == created["signature"]
    assert traded["created_mint"] == created["disposable_mint"]
    assert traded["created_curve"] == created["accounts"]["bonding_curve"]["address"]
    create_tx = Transaction.from_bytes(base64.b64decode(created["transaction_base64"]))
    assert all(create_tx.verify_with_results()) and len(create_tx.signatures) == 2
    assert str(create_tx.signatures[0]) == created["signature"]
    assert created["signature_verified"] and created["simulation_error"] is None
    assert created["committed_error"] is None
    mint = raw(created["accounts"]["mint"])
    curve = raw(created["accounts"]["bonding_curve"])
    curve_ata = raw(created["accounts"]["associated_bonding_curve"])
    assert created["accounts"]["mint"]["owner"] == \
           "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
    assert created["accounts"]["bonding_curve"]["owner"] == created["program"]
    assert u64(mint, 36) == u64(curve_ata, 64) == 1_000_000_000_000_000
    assert [u64(curve, at) for at in (8, 16, 24, 32)] == [
        1_073_000_000_000_000, 30_000_000_000,
        793_100_000_000_000, 0]
    assert curve[48] == 0
    assert Pubkey.from_bytes(curve_ata[:32]) == \
           Pubkey.from_string(traded["created_mint"])
    assert Pubkey.from_bytes(curve_ata[32:64]) == \
           Pubkey.from_string(traded["created_curve"])

    steps = traded["steps"]
    assert [row["label"] for row in steps] == ["create_user_base_ata",
        "buy_v3_tight_max_rollback", "buy_v3", "sell_v3_high_min_rollback",
        "sell_v3"]
    assert traded["base_amount_out"] == 1_000_000_000
    assert traded["base_amount_sold"] == 500_000_000
    assert traded["max_sol_cost"] == 1_000_000_000
    signatures = {created["signature"]}
    for i, row in enumerate(steps):
        tx = Transaction.from_bytes(base64.b64decode(row["transaction_base64"]))
        assert all(tx.verify_with_results())
        assert str(tx.signatures[0]) == row["signature"]
        assert row["signature"] not in signatures
        signatures.add(row["signature"])
        assert row["simulation_error"] == row["committed_error"]
        if i:
            assert steps[i - 1]["after"] == row["before"]
        if i in (1, 3):
            expected = 6002 if i == 1 else 6003
            assert row["committed_error"] == {"InstructionError": [1, {"Custom": expected}]}
            for name in row["before"]:
                if name == "user":
                    assert row["before"][name]["lamports"] - \
                           row["after"][name]["lamports"] == 5000
                    assert row["before"][name]["data_sha256"] == \
                           row["after"][name]["data_sha256"]
                else:
                    assert row["before"][name] == row["after"][name]
        else:
            assert row["committed_error"] is None
    assert steps[0]["before"]["user_base"] is None
    assert steps[0]["after"]["user_base"]["token_amount"] == 0
    assert steps[2]["before"]["volume"] is None
    assert steps[2]["after"]["volume"] is not None

    for row, base_change, user_lamport_change, curve_lamport_change, buyback_change, \
        quote_reserve_change, protocol_fee_change, creator_fee_change in (
            (steps[2], 1_000_000_000, -1_877_710, 28_177, 133, 27_960, 84, 133),
            (steps[4], -500_000_000, 8_804, -13_870, 66, -13_979, 42, 67),
    ):
        before, after = row["before"], row["after"]
        assert after["user_base"]["token_amount"] - before["user_base"]["token_amount"] == base_change
        assert after["curve_base"]["token_amount"] - before["curve_base"]["token_amount"] == -base_change
        assert before["user_base"]["token_amount"] + before["curve_base"]["token_amount"] == \
               after["user_base"]["token_amount"] + after["curve_base"]["token_amount"]
        assert after["user"]["lamports"] - before["user"]["lamports"] == user_lamport_change
        assert after["curve"]["lamports"] - before["curve"]["lamports"] == curve_lamport_change
        assert after["buyback"]["lamports"] - before["buyback"]["lamports"] == buyback_change
        assert lamport_total(before) - lamport_total(after) == 5000
        before_curve, after_curve = raw(before["curve"]), raw(after["curve"])
        assert u64(after_curve, 16) - u64(before_curve, 16) == quote_reserve_change
        assert u64(after_curve, 32) - u64(before_curve, 32) == quote_reserve_change
        assert u64(after_curve, 125) - u64(before_curve, 125) == protocol_fee_change
        assert u64(after_curve, 133) - u64(before_curve, 133) == creator_fee_change
        assert curve_lamport_change == quote_reserve_change + \
               protocol_fee_change + creator_fee_change
        for name in ("mint", "quote_mint", "global", "fee_config"):
            assert before[name] == after[name]
    assert steps[2]["before"]["curve_base"]["token_amount"] - \
           steps[2]["after"]["curve_base"]["token_amount"] == 1_000_000_000
    assert steps[4]["after"]["user_base"]["token_amount"] == 500_000_000
    print(json.dumps({"verified": True, "create_signature": created["signature"],
                      "signed_followup_transactions": len(steps),
                      "buy_base_raw": 1_000_000_000,
                      "sell_base_raw": 500_000_000,
                      "create_receipt": str(CREATE), "trade_receipt": str(TRADES)}))


if __name__ == "__main__":
    main()
