"""Verify saved signed offline Pump.fun config-write and guard receipts."""

import base64
import hashlib
import json
import struct
from pathlib import Path

from solders.pubkey import Pubkey
from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
RECEIPT = LANE / "admin-signed-surfpool.json"
AUTH_OFFSET = {"pump": 9, "pump_amm": 8, "pump_fees": 9}
ORDER = ("pump", "pump_amm", "pump_fees")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def data(row):
    raw = base64.b64decode(row["data_base64"])
    assert sha(raw) == row["data_sha256"]
    return raw


def main():
    report = json.loads(RECEIPT.read_text())
    manifest = {Path(row["path"]).stem: row for row in json.loads(
        (LANE / "program-manifest.json").read_text())["programs"]}
    inventory = {row["name"]: row for row in json.loads(
        (LANE / "elf-inventory.json").read_text())["programs"]}
    captures = {row["program_name"]: row for row in json.loads(
        (LANE / "config-snapshot.json").read_text())["accounts"]}
    assert set(manifest) == set(inventory) == set(captures) == set(report["programs"]) == set(ORDER)
    assert report["environment"] == "offline Surfpool :memory: loopback"
    assert len(report["cases"]) == 6
    setup = report["cases"][0]["before"]
    for name in ORDER:
        item = report["programs"][name]
        assert item["program"] == manifest[name]["program"]
        assert item["payload_sha256"] == sha((ROOT / manifest[name]["path"]).read_bytes())
        assert item["loaded_elf_extent"] == inventory[name]["elf_extent_bytes"]
        original = base64.b64decode(captures[name]["data_base64"])
        assert sha(original) == captures[name]["data_sha256"] == item["captured_config_sha256"]
        assert item["config_address"] == captures[name]["address"]
        assert setup[name]["owner"] == item["program"]
        copied = bytearray(original)
        copied[AUTH_OFFSET[name]:AUTH_OFFSET[name] + 32] = bytes(
            Pubkey.from_string(item["synthetic_authority"]))
        assert data(setup[name]) == bytes(copied)
        assert setup[name]["lamports"] == captures[name]["lamports"]

    previous = None
    for index, row in enumerate(report["cases"]):
        name = ORDER[index // 2]
        authorized = index % 2 == 1
        assert row["label"] == name + ("_authorized_write" if authorized else "_wrong_authority")
        if previous is not None:
            assert previous == row["before"]
        tx = Transaction.from_bytes(base64.b64decode(row["transaction_base64"]))
        assert all(tx.verify_with_results())
        assert str(tx.signatures[0]) == row["signature"]
        assert row["signature_verified"]
        assert row["simulation_error"] == row["committed_error"]
        assert (row["committed_error"] is None) == authorized
        assert row["payer_fee_lamports"] == 5000
        if not authorized:
            assert row["before"] == row["after"]
        else:
            for other in ORDER:
                if other != name:
                    assert row["before"][other] == row["after"][other]
            before = data(row["before"][name])
            after = data(row["after"][name])
            changed = [offset for offset, (a, b) in enumerate(zip(before, after)) if a != b]
            assert changed == row["changed_config_offsets"]
            assert len(before) == len(after)
            if name == "pump":
                assert changed == [len(before) - 1] and before[-1] == 2 and after[-1] == 1
            elif name == "pump_amm":
                assert changed == [56] and before[56] == 0 and after[56] == 8
            else:
                assert set(changed).issubset(set(range(74, 82)))
                assert struct.unpack_from("<Q", before, 74)[0] == 0
                assert struct.unpack_from("<Q", after, 74)[0] == 600
        previous = row["after"]
    print(json.dumps({"verified": True, "signed_transactions": len(report["cases"]),
                      "successful_writes": len(ORDER),
                      "wrong_authority_rollbacks": len(ORDER),
                      "receipt": str(RECEIPT)}))


if __name__ == "__main__":
    main()
