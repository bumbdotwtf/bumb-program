"""Verify signed PumpSwap v2 trades on the pool created by local migrate_v2."""

import base64
import hashlib
import json
import struct
from pathlib import Path

from solders.pubkey import Pubkey
from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
RECEIPT = LANE / "post-migration-amm-v2-signed-surfpool.json"
AMM_IDL = ROOT / "third_party/pump-public-docs/idl/pump_amm.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw(row):
    data = base64.b64decode(row["data_base64"])
    assert sha(data) == row["data_sha256"]
    return data


def totals(state):
    return {"base": state["user_base"]["token_amount"] +
                    state["pool_base"]["token_amount"],
            "quote": sum(state[name]["token_amount"] for name in
                         ("user_quote", "pool_quote", "buyback", "boost_vault"))}


def main():
    receipt = json.loads(RECEIPT.read_text())
    migrated = json.loads((LANE / "curve-migrate-v2-signed-surfpool.json").read_text())
    fixture = json.loads((LANE / "amm-v2-trade-fixture.json").read_text())
    manifest = {Path(row["path"]).stem: row for row in json.loads(
        (LANE / "program-manifest.json").read_text())["programs"]}
    idl = json.loads(AMM_IDL.read_text())
    amm = Pubkey.from_string(receipt["amm_program"])
    assert receipt["environment"] == migrated["environment"] == \
           "offline Surfpool :memory: loopback"
    assert receipt["fresh_pool"] == migrated["pool"]
    assert receipt["fresh_mint"] == migrated["fresh_mint"]
    assert receipt["migration_signature"] == migrated["migration"]["signature"]
    assert receipt["amm_program"] == manifest["pump_amm"]["program"]
    assert receipt["amm_program_sha256"] == sha(
        (ROOT / manifest["pump_amm"]["path"]).read_bytes())
    assert receipt["base_amount_bought"] == 1_000_000_000
    assert receipt["base_amount_sold"] == 500_000_000
    steps = receipt["steps"]
    assert [row["label"] for row in steps] == [
        "create_and_fund_user_wsol", "fresh_pool_buy_v2_tight_max_rollback",
        "fresh_pool_buy_v2", "fresh_pool_sell_v2_high_min_rollback",
        "fresh_pool_sell_v2"]
    initial = steps[0]["before"]
    prior = migrated["migration"]["after"]
    for name in ("user", "pool", "user_base", "pool_base", "pool_quote",
                 "boost_vault", "global_config"):
        old_name = "amm_global_config" if name == "global_config" else name
        assert initial[name] == prior[old_name]
    assert initial["user_quote"] is None
    assert initial["buyback"]["data_sha256"] == \
           fixture["accounts"]["buyback_fee_recipient"]["data_sha256"]
    assert initial["fee_config"]["data_sha256"] == \
           fixture["accounts"]["fee_config"]["data_sha256"]
    assert initial["volume"] is None
    signatures = set()
    for index, step in enumerate(steps):
        tx = Transaction.from_bytes(base64.b64decode(step["transaction_base64"]))
        assert all(tx.verify_with_results())
        assert str(tx.signatures[0]) == step["signature"]
        assert step["signature"] not in signatures
        signatures.add(step["signature"])
        assert step["simulation_error"] == step["committed_error"]
        if index:
            assert steps[index - 1]["after"] == step["before"]
        if index:
            assert tx.message.account_keys[
                tx.message.instructions[-1].program_id_index] == amm
            name = "buy_v2" if index in (1, 2) else "sell_v2"
            discriminator = bytes(next(ix["discriminator"] for ix in
                idl["instructions"] if ix["name"] == name))
            assert bytes(tx.message.instructions[-1].data).startswith(discriminator)
        if index in (1, 3):
            assert step["committed_error"] == {
                "InstructionError": [1, {"Custom": 6004}]}
            for name in step["before"]:
                if name == "user":
                    assert step["before"][name]["lamports"] - \
                           step["after"][name]["lamports"] == 5000
                else:
                    assert step["before"][name] == step["after"][name]
        else:
            assert step["committed_error"] is None
    funded = steps[0]
    assert funded["after"]["user_quote"]["token_amount"] == 1_000_000_000
    assert funded["after"]["pool"] == funded["before"]["pool"]
    assert funded["after"]["pool_base"] == funded["before"]["pool_base"]
    assert funded["after"]["pool_quote"] == funded["before"]["pool_quote"]
    for step in (steps[2], steps[4]):
        before, after = step["before"], step["after"]
        assert totals(before) == totals(after)
        assert before["global_config"] == after["global_config"]
        assert before["fee_config"] == after["fee_config"]
        assert before["boost_vault"] == after["boost_vault"]
        old, new = raw(before["pool"]), raw(after["pool"])
        protocol = struct.unpack_from("<Q", new, 271)[0] - \
                   struct.unpack_from("<Q", old, 271)[0]
        creator = struct.unpack_from("<Q", new, 279)[0] - \
                  struct.unpack_from("<Q", old, 279)[0]
        virtual = int.from_bytes(new[245:261], "little", signed=True) - \
                  int.from_bytes(old[245:261], "little", signed=True)
        assert protocol > 0 and creator > 0
        assert virtual == -(protocol + creator)
    bought, sold = steps[2], steps[4]
    assert bought["after"]["volume"] is not None
    assert bought["after"]["user_base"]["token_amount"] - \
           bought["before"]["user_base"]["token_amount"] == 1_000_000_000
    assert sold["before"]["user_base"]["token_amount"] - \
           sold["after"]["user_base"]["token_amount"] == 500_000_000
    quote_spent = bought["before"]["user_quote"]["token_amount"] - \
                  bought["after"]["user_quote"]["token_amount"]
    quote_received = sold["after"]["user_quote"]["token_amount"] - \
                     sold["before"]["user_quote"]["token_amount"]
    assert quote_spent == 415_919 and quote_received == 202_821
    print(json.dumps({"verified": True, "signed_transactions": len(steps),
                      "fresh_pool": receipt["fresh_pool"],
                      "buy_quote_spent_raw": quote_spent,
                      "sell_quote_received_raw": quote_received,
                      "receipt": str(RECEIPT)}))


if __name__ == "__main__":
    main()
