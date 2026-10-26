"""Offline verification of signed Pump Fees synthetic referral-vault payout."""

import base64
import hashlib
import json
from pathlib import Path

from solders.pubkey import Pubkey
from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
RECEIPT = LANE / "fees-withdraw-signed-surfpool.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw(row):
    value = base64.b64decode(row["data_base64"])
    assert sha(value) == row["data_sha256"]
    return value


def main():
    receipt = json.loads(RECEIPT.read_text())
    fixture = json.loads((LANE / "amm-v2-trade-fixture.json").read_text())
    manifest = next(row for row in json.loads((LANE / "program-manifest.json").read_text())["programs"]
                    if row["program"] == receipt["program"])
    assert sha((ROOT / manifest["path"]).read_bytes()) == receipt["payload_sha256"]
    assert receipt["environment"] == "offline Surfpool :memory: loopback"
    assert receipt["initial_vault_raw"] == 1_000_000
    assert receipt["source_mint_sha256"] == fixture["accounts"]["quote_mint"]["data_sha256"]
    assert receipt["source_token_layout_sha256"] == \
           fixture["accounts"]["pool_quote_token_account"]["data_sha256"]
    assert receipt["accounts"]["quote_mint"] == fixture["keys"]["quote_mint"]
    cases = receipt["cases"]
    assert [row["label"] for row in cases] == ["unsigned_user_rejected",
        "wrong_user_rejected", "redirected_recipient_rejected", "withdraw"]
    expected_errors = [3010, 2006, 2015, None]
    signatures = set()
    for index, row in enumerate(cases):
        tx = Transaction.from_bytes(base64.b64decode(row["transaction_base64"]))
        assert all(tx.verify_with_results())
        assert str(tx.signatures[0]) == row["signature"]
        assert row["signature"] not in signatures
        signatures.add(row["signature"])
        assert row["simulation_error"] == row["committed_error"]
        assert row["payer_lamports_delta"] == -5000
        if index:
            assert cases[index - 1]["after"] == row["before"]
        code = expected_errors[index]
        if code is not None:
            assert row["simulation_error"] == {"InstructionError": [0, {"Custom": code}]}
            assert row["before"] == row["after"]
        else:
            assert row["simulation_error"] is None
    before, after = cases[-1]["before"], cases[-1]["after"]
    assert before["referral_vault"] == after["referral_vault"]
    assert before["referral_vault"]["owner"] == \
           "11111111111111111111111111111111"
    assert before["outsider_ata"] == after["outsider_ata"]
    vault_before = before["vault_ata"]["token_amount"]
    vault_after = after["vault_ata"]["token_amount"]
    user_before = before["user_ata"]["token_amount"]
    user_after = after["user_ata"]["token_amount"]
    assert (vault_before, vault_after, user_before, user_after) == \
           (1_000_000, 0, 0, 1_000_000)
    assert before["vault_ata"]["lamports"] - after["vault_ata"]["lamports"] == 1_000_000
    assert after["user_ata"]["lamports"] - before["user_ata"]["lamports"] == 1_000_000
    assert before["vault_ata"]["lamports"] + before["user_ata"]["lamports"] == \
           after["vault_ata"]["lamports"] + after["user_ata"]["lamports"]
    vault_data = raw(before["vault_ata"])
    user_data = raw(before["user_ata"])
    assert Pubkey.from_bytes(vault_data[32:64]) == \
           Pubkey.from_string(receipt["accounts"]["referral_vault"])
    assert Pubkey.from_bytes(user_data[32:64]) == \
           Pubkey.from_string(receipt["synthetic_user"])
    assert vault_data[:32] == user_data[:32] == bytes(
        Pubkey.from_string(receipt["accounts"]["quote_mint"]))
    print(json.dumps({"verified": True, "signed_transactions": len(cases),
                      "payout_raw": user_after - user_before,
                      "rejections_rolled_back": 3,
                      "receipt": str(RECEIPT)}))


if __name__ == "__main__":
    main()
