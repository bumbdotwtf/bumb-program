"""Re-execute and verify the signed Pump token-incentive claim differential."""

import argparse
import base64
import gzip
import json
import struct
from pathlib import Path

from solders.transaction import Transaction

import pump_claim_token_incentives_differential as diff


LOG = diff.ROOT / "repro/pump/claim-token-incentives/build.log.gz"
SECOND_BUILD = diff.ROOT / "repro/pump/claim-token-incentives/build-second-comparison.json"
SECOND_LOG = diff.ROOT / "repro/pump/claim-token-incentives/build-second.log.gz"
BUILD_REPRO = diff.ROOT / "repro/pump/claim-token-incentives/build-reproducibility.json"
INHERITED = diff.ROOT / "repro/pump/claim-token-incentives/inherited-regressions.json"
EXPECTED_ERRORS = {
    "vault_underfunded": 1,
    "wrong_global_owner": 3007,
    "wrong_user_owner": 3007,
    "wrong_global_pda": 2006,
    "wrong_user_pda": 2006,
    "wrong_mint": 3007,
    "wrong_token_program": 3008,
    "wrong_event_authority": 2006,
    "wrong_program_account": 3008,
    "read_only_user_volume": 2000,
}
EVENT_CPI_DISCRIMINATOR = bytes.fromhex("e445a52e51cb9a1d")


def account_bytes(row):
    data = base64.b64decode(row["data_base64"])
    assert diff.sha(data) == row["data_sha256"]
    return data


def token_amount(row):
    return struct.unpack_from("<Q", account_bytes(row), 64)[0]


def assert_signature(row):
    tx = Transaction.from_bytes(base64.b64decode(row["transaction_base64"]))
    assert all(tx.verify_with_results())
    assert str(tx.signatures[0]) == row["signature"]


def assert_event_and_cpis(row, event_discriminator, keys):
    before, after = row["before"], row["after"]
    assert len(row["event_data_base64"]) == 1 and len(row["inner"]) == 2
    event = base64.b64decode(row["event_data_base64"][0])
    assert len(event) == 104 and event[:8] == event_discriminator
    assert event[8:40] == bytes(keys["user"])
    assert event[40:72] == bytes(keys["mint"])
    amount, timestamp, claimed, volume = struct.unpack_from("<QqQQ", event, 72)
    assert amount > 0 and timestamp == row["case"].get("now", 10)
    assert claimed == row["user_after"][2] and volume == row["user_after"][3]
    assert token_amount(after["user_ata"]) - token_amount(before["user_ata"]) == amount
    assert token_amount(before["global_ata"]) - token_amount(after["global_ata"]) == amount
    transfer, event_cpi = row["inner"]
    assert transfer["program"] == str(diff.TOKEN)
    assert transfer["accounts"] == [str(keys["global_ata"]), str(keys["mint"]),
                                     str(keys["user_ata"]), str(diff.GLOBAL_VOLUME)]
    assert bytes.fromhex(transfer["data_hex"]) == bytes([12]) + \
           struct.pack("<Q", amount) + bytes([6])
    assert event_cpi["program"] == str(diff.PROGRAM)
    assert event_cpi["accounts"] == [str(diff.EVENT_AUTHORITY)]
    assert bytes.fromhex(event_cpi["data_hex"]) == EVENT_CPI_DISCRIMINATOR + event
    assert any("Instruction: TransferChecked" in line
               for line in row["relevant_logs"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, default=diff.OUT)
    args = parser.parse_args()
    report = json.loads(args.receipt.read_text())
    build = json.loads(diff.BUILD.read_text())
    second_build = json.loads(SECOND_BUILD.read_text())
    repro = json.loads(BUILD_REPRO.read_text())
    assert report["baseline_commit"] == "4ffe8bd88761059693e481ae972443c10204f7af"
    assert report["target_sha256"] == diff.sha(diff.ORIGINAL.read_bytes())
    assert report["candidate_sha256"] == diff.sha(args.candidate.read_bytes())
    assert report["build_receipt_sha256"] == diff.sha(diff.BUILD.read_bytes())
    assert report["idl_sha256"] == diff.sha(diff.IDL.read_bytes())
    assert report["fixture_sha256"] == diff.sha(diff.FIXTURE.read_bytes())
    assert report["script_sha256"] == diff.sha(Path(diff.__file__).read_bytes())
    assert report["dependency_sha256"] == {name: diff.sha((diff.ROOT /
        f"evidence/dependencies/{name}/deployed.so").read_bytes())
        for name in ("spl_token_2022", "associated_token")}
    assert all(diff.sha((diff.ROOT / path).read_bytes()) == expected
               for path, expected in report["source_sha256"].items())
    assert all(diff.sha((diff.ROOT / path).read_bytes()) == expected
               for path, expected in build["source_sha256"].items())
    assert diff.sha(gzip.decompress(LOG.read_bytes())) == build["build_log_sha256"]
    assert diff.sha(gzip.decompress(SECOND_LOG.read_bytes())) == second_build["build_log_sha256"]
    assert repro["build_receipt_sha256"] == [diff.sha(diff.BUILD.read_bytes()),
                                              diff.sha(SECOND_BUILD.read_bytes())]
    assert repro["source_sha256"] == build["source_sha256"] == second_build["source_sha256"]
    assert repro["candidate_sha256"] == [report["candidate_sha256"]] * 2
    assert repro["builds_identical"] and not repro["deployed_byte_match"]
    inherited = json.loads(INHERITED.read_text())
    assert inherited["baseline_commit"] == report["baseline_commit"]
    assert inherited["candidate_sha256"] == report["candidate_sha256"]
    assert inherited["target_sha256"] == report["target_sha256"]
    assert inherited["total_cases"] == 9161 and inherited["suite_count"] == 36
    assert [entry["name"] for entry in inherited["receipts"]] == [
        "maintained", "holder_distribution", "nested_create", "quote_control"]
    assert [entry["cases"] for entry in inherited["receipts"]] == \
        [7957, 649, 48, 507]
    for entry in inherited["receipts"]:
        compressed = (INHERITED.parent / entry["file"]).read_bytes()
        raw = gzip.decompress(compressed)
        assert diff.sha(compressed) == entry["compressed_sha256"]
        assert diff.sha(raw) == entry["json_sha256"] and len(raw) == entry["json_bytes"]
        selected = json.loads(raw)
        if entry["name"] == "quote_control":
            assert selected["cases"] == entry["cases"] == len(selected["results"])
            assert selected["mismatches"] == 0
            for path, expected in selected["bound_inputs_sha256"].items():
                if path == "work/claim-pr-candidate/pump_recovered.so":
                    assert expected == report["candidate_sha256"]
                else:
                    assert diff.sha((diff.ROOT / path).read_bytes()) == expected
        else:
            assert selected["candidate_sha256"] == report["candidate_sha256"]
            assert selected["original_sha256"] == report["target_sha256"]
            assert selected["case_count"] == entry["cases"] and not selected["mismatches"]
            if entry["name"] == "maintained":
                assert len(selected["suites"]) == 33
                assert sum(suite["case_count"] for suite in selected["suites"].values()) == 7957
                assert all(not suite.get("mismatches", suite.get("failures", []))
                           for suite in selected["suites"].values())
                assert all(diff.sha((diff.ROOT / "scripts" / name).read_bytes()) == digest
                           for name, digest in selected["script_sha256"].items())
            else:
                assert len(selected["cases"]) == entry["cases"]
    assert build["selected_toolchain"] == "v1.44"
    assert build["comparison"]["candidate_sha256"] == report["candidate_sha256"]
    assert build["comparison"]["original_sha256"] == report["target_sha256"]
    assert not build["comparison"]["full_byte_equality"]
    assert report["signed_local"] and report["offline_only"]
    idl = json.loads(diff.IDL.read_text())
    event_discriminator = bytes(next(item for item in idl["events"]
        if item["name"] == "ClaimTokenIncentivesEvent")["discriminator"])
    _, keys, _, user_volume, global_ata = diff.fixture_data()
    keys["user_ata"] = keys["user_base"]
    keys["global_ata"] = global_ata
    assert user_volume == keys["volume"]
    rows = report["cases"]
    assert len(rows) == report["summary"]["cases"] == len(diff.CASES) == 60
    assert [row["case"] for row in rows] == list(diff.CASES)
    successes = 0
    events = 0
    for row in rows:
        case = row["case"]
        target = diff.run_case(diff.ORIGINAL, case)
        candidate = diff.run_case(args.candidate, case)
        assert target == row["target"] and candidate == row["candidate"]
        assert_signature(target)
        assert_signature(candidate)
        assert not row["differences"]
        for field in ("error", "before", "after", "event_data_base64", "inner",
                      "signature", "transaction_base64"):
            assert target[field] == candidate[field], (case["name"], field)
        assert target["error_code"] == EXPECTED_ERRORS.get(case["name"])
        assert target["before"]["payer"]["lamports"] - \
               target["after"]["payer"]["lamports"] == 5_000
        assert target["before"]["global_volume"] == \
               target["after"]["global_volume"]
        assert target["before"]["mint"] == target["after"]["mint"]
        assert any("Instruction: ClaimTokenIncentives" in line
                   for line in target["relevant_logs"])
        if target["success"]:
            successes += 1
            if target["event_data_base64"]:
                events += 1
                assert_event_and_cpis(target, event_discriminator, keys)
            else:
                assert not target["inner"]
                assert target["before"]["user_ata"] == target["after"]["user_ata"]
                assert target["before"]["global_ata"] == target["after"]["global_ata"]
        else:
            assert target["before"]["user_ata"] == target["after"]["user_ata"]
            assert target["before"]["global_ata"] == target["after"]["global_ata"]
            assert target["before"]["user_volume"] == target["after"]["user_volume"]
            assert not target["event_data_base64"]
            if case["name"] in ("now_day_30", "now_day_31"):
                assert "Fieldless(ProgramFailedToComplete)" in target["error"]
            elif case["name"] == "vault_underfunded":
                assert len(target["inner"]) == 1
            else:
                assert not target["inner"]
    assert successes == report["summary"]["target_successes"] == 48
    assert report["summary"]["matched"] == 60
    print(json.dumps({"verified": True, "signed_cases": len(rows),
                      "successes": successes, "payout_events": events,
                      "rollbacks": len(rows) - successes,
                      "candidate_sha256": report["candidate_sha256"]}))


if __name__ == "__main__":
    main()
