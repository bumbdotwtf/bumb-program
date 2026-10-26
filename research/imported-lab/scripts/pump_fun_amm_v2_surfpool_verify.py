"""Offline verifier for signed PumpSwap v2 buy/sell balance receipts."""

import base64
import hashlib
import json
import struct
from pathlib import Path

from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
RECEIPT = LANE / "amm-buy-v2-signed-surfpool.json"
TOKEN_NAMES = ("user_base", "pool_base", "user_quote", "pool_quote",
               "buyback_quote")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw(row):
    value = base64.b64decode(row["data_base64"])
    assert sha(value) == row["data_sha256"]
    return value


def totals(state):
    return {"base": state["user_base"]["token_amount"] +
                    state["pool_base"]["token_amount"],
            "quote": sum(state[name]["token_amount"] for name in
                         ("user_quote", "pool_quote", "buyback_quote"))}


def main():
    receipt = json.loads(RECEIPT.read_text())
    fixture_path = LANE / "amm-v2-trade-fixture.json"
    assert sha(fixture_path.read_bytes()) == receipt["fixture_sha256"]
    fixture = json.loads(fixture_path.read_text())
    manifest = {Path(row["path"]).stem: row for row in json.loads(
        (LANE / "program-manifest.json").read_text())["programs"]}
    assert receipt["environment"] == "offline Surfpool :memory: loopback"
    assert receipt["pool"] == fixture["pool"]
    assert receipt["captured_pool_slot"] == fixture["accounts"]["pool"]["slot"]
    assert receipt["program_hashes"] == {
        name: manifest[name]["payload_sha256"] for name in ("pump_amm", "pump_fees")}
    for name in ("pump_amm", "pump_fees"):
        assert sha((ROOT / manifest[name]["path"]).read_bytes()) == \
               receipt["program_hashes"][name]
    assert receipt["base_amount_out"] == 10_000_000_000
    assert receipt["base_amount_sold"] == 5_000_000_000
    assert receipt["max_quote_amount_in"] == 1_000_000_000
    cases = receipt["cases"]
    assert [case["label"] for case in cases] == [
        "unsigned_trader_rejected", "max_quote_one_rollback", "buy_v2",
        "sell_v2_high_min_rollback", "sell_v2"]
    first = cases[0]["before"]
    for name, key in (("pool", "pool"),
                      ("pool_base", "pool_base_token_account"),
                      ("pool_quote", "pool_quote_token_account"),
                      ("buyback_quote", "buyback_fee_recipient"),
                      ("fee_config", "fee_config")):
        assert first[name]["data_sha256"] == fixture["accounts"][key]["data_sha256"]
    assert first["volume"] is None
    assert raw(first["pool"])[244] == 0  # captured non-cashback pool
    signatures = set()
    for index, case in enumerate(cases):
        tx = Transaction.from_bytes(base64.b64decode(case["transaction_base64"]))
        assert all(tx.verify_with_results())
        assert str(tx.signatures[0]) == case["signature"]
        assert case["signature"] not in signatures
        signatures.add(case["signature"])
        assert case["simulation_error"] == case["committed_error"]
        if index:
            assert cases[index - 1]["after"] == case["before"]
        if index in (0, 1, 3):
            assert case["simulation_error"] is not None
            assert case["before"] == case["after"]
            assert case["payer_lamports_spent"] == 5000
        else:
            assert case["simulation_error"] is None
            assert totals(case["before"]) == totals(case["after"])
            for name in ("global_config", "fee_config"):
                assert case["before"][name] == case["after"][name]
            before_pool = raw(case["before"]["pool"])
            after_pool = raw(case["after"]["pool"])
            protocol_delta = struct.unpack_from("<Q", after_pool, 271)[0] - \
                             struct.unpack_from("<Q", before_pool, 271)[0]
            creator_delta = struct.unpack_from("<Q", after_pool, 279)[0] - \
                            struct.unpack_from("<Q", before_pool, 279)[0]
            virtual_delta = int.from_bytes(after_pool[245:261], "little", signed=True) - \
                            int.from_bytes(before_pool[245:261], "little", signed=True)
            assert protocol_delta > 0 and creator_delta > 0
            assert virtual_delta == -(protocol_delta + creator_delta)
    buy, sell = cases[2], cases[4]
    assert buy["after"]["volume"] is not None
    assert buy["payer_lamports_spent"] == 1_849_400  # fee plus local UVA rent
    assert buy["after"]["user_base"]["token_amount"] - \
           buy["before"]["user_base"]["token_amount"] == 10_000_000_000
    buy_spent = buy["before"]["user_quote"]["token_amount"] - \
                buy["after"]["user_quote"]["token_amount"]
    assert buy_spent == 1_847_796
    assert sell["before"]["user_base"]["token_amount"] - \
           sell["after"]["user_base"]["token_amount"] == 5_000_000_000
    sell_received = sell["after"]["user_quote"]["token_amount"] - \
                    sell["before"]["user_quote"]["token_amount"]
    assert sell_received == 901_089
    print(json.dumps({"verified": True, "signed_transactions": len(cases),
                      "buy_spent_quote_raw": buy_spent,
                      "sell_received_quote_raw": sell_received,
                      "receipt": str(RECEIPT)}))


if __name__ == "__main__":
    main()
