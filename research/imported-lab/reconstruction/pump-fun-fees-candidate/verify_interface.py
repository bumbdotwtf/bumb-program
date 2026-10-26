"""Check all IDL selectors reach fail-closed candidate handlers in LiteSVM."""

import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from svm_lab import Account, Instruction, PAYER, Pubkey, ROOT as LAB_ROOT, SYSTEM, Transaction, meta, vm_new  # noqa: E402
from solders.transaction_metadata import FailedTransactionMetadata  # noqa: E402


IDL = ROOT / "third_party/pump-public-docs/idl/pump_fees.json"
CANDIDATE = PACKAGE / "target/deploy/pump_fees_candidate.so"
OUT = PACKAGE / "interface-verification.json"
PID = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_argument(spec):
    if isinstance(spec, str):
        if spec in ("pubkey",):
            return bytes(32)
        if spec in ("string", "bytes"):
            return bytes(4)
        sizes = {"bool": 1, "u8": 1, "i8": 1, "u16": 2, "i16": 2,
                 "u32": 4, "i32": 4, "u64": 8, "i64": 8,
                 "u128": 16, "i128": 16}
        return bytes(sizes[spec])
    if "option" in spec:
        return b"\x00"
    if "vec" in spec:
        return bytes(4)
    if "array" in spec:
        child, count = spec["array"]
        return zero_argument(child) * count
    if "defined" in spec:
        name = spec["defined"]["name"]
        return {"OptionBool": bytes(1), "Fees": bytes(24),
                "FeeTier": bytes(40), "Shareholder": bytes(34)}[name]
    raise ValueError(spec)


def execute(instruction):
    vm = vm_new()
    vm.add_program_from_file(PID, CANDIDATE)
    accounts = []
    for index, row in enumerate(instruction["accounts"]):
        name = row["name"]
        if row.get("signer"):
            key = PAYER.pubkey()
        elif name == "system_program":
            key = SYSTEM
        else:
            key = Pubkey.from_bytes(hashlib.sha256(
                f"{instruction['name']}:{index}:{name}".encode()).digest())
            vm.set_account(key, Account(1_000_000, b"", SYSTEM))
        accounts.append(meta(key, bool(row.get("writable")),
                             bool(row.get("signer"))))
    args = b"".join(zero_argument(row["type"]) for row in instruction["args"])
    data = bytes(instruction["discriminator"]) + args
    tx = Transaction.new_signed_with_payer(
        [Instruction(PID, data, accounts)], PAYER.pubkey(), [PAYER],
        vm.latest_blockhash())
    assert all(tx.verify_with_results())
    result = vm.simulate_transaction(tx)
    assert isinstance(result, FailedTransactionMetadata)
    error = str(result.err())
    assert "InstructionErrorCustom(6000)" in error, (instruction["name"], error)
    return {"instruction": instruction["name"],
            "discriminator_hex": bytes(instruction["discriminator"]).hex(),
            "idl_account_count": len(accounts), "zero_argument_bytes": len(args),
            "signature_verified": True, "candidate_error": error,
            "unsupported_body_reached": True,
            "compute_units": result.meta().compute_units_consumed()}


def main():
    assert LAB_ROOT == ROOT
    idl = json.loads(IDL.read_text())
    assert sha(IDL) == \
        "6b9fa3eccc6e06273076a47b581f9fcb9e531bb7c3c88acbcd44db55a4002b29"
    assert len(idl["instructions"]) == 31
    for item in idl["instructions"]:
        assert bytes(item["discriminator"]) == hashlib.sha256(
            f"global:{item['name']}".encode()).digest()[:8]
    rows = [execute(item) for item in idl["instructions"]]
    assert len(rows) == len({row["instruction"] for row in rows}) == 31
    report = {"scope": "Local candidate only, not deployed Pump Fees. All 31 IDL selectors and zero-valued argument encodings reach intentionally unsupported Anchor bodies under constructed local accounts. This proves scaffold dispatch, not target behavior or byte equality.",
              "idl_sha256": sha(IDL), "candidate_sha256": sha(CANDIDATE),
              "selector_count": len(rows), "unsupported_reached": len(rows),
              "cases": rows}
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"selector_count": len(rows),
                      "unsupported_reached": len(rows),
                      "candidate_sha256": report["candidate_sha256"]}))


if __name__ == "__main__":
    main()
