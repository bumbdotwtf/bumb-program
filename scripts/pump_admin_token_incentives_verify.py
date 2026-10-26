"""Independent signed offline replay of Pump incentive scheduler evidence."""

import argparse
import base64
import gzip
import json
from pathlib import Path

import pump_admin_token_incentives_differential as diff


FINANCIAL_ACCOUNTS = (
    "global", "global_volume_accumulator", "mint",
    "global_incentive_token_account", "canonical_global",
    "canonical_volume", "canonical_vault",
)


def main(receipt_path=diff.OUTPUT, candidate_path=diff.CANDIDATE,
         build_path=diff.BUILD, expected_baseline="4ffe8bd88761059693e481ae972443c10204f7af"):
    receipt_path, candidate_path, build_path = map(Path,
                                                   (receipt_path, candidate_path, build_path))
    encoded = receipt_path.read_bytes()
    receipt = json.loads(gzip.decompress(encoded) if receipt_path.suffix == ".gz"
                         else encoded)
    assert receipt["baseline_commit"] == expected_baseline
    assert receipt["target_sha256"] == diff.sha(diff.TARGET)
    assert receipt["candidate_sha256"] == diff.sha(candidate_path)
    assert receipt["build_comparison_sha256"] == diff.sha(build_path)
    build = json.loads(build_path.read_text())
    assert build["selected_toolchain"] == "v1.44"
    assert build["comparison"]["candidate_sha256"] == receipt["candidate_sha256"]
    assert all(checksum == diff.sha(diff.ROOT / path)
               for path, checksum in build["source_sha256"].items())
    assert build["build_log_sha256"] == diff.sha(gzip.decompress(
        (build_path.parent / "build.log.gz").read_bytes()))
    if receipt.get("second_clean_build") is not None:
        second = receipt["second_clean_build"]
        second_path = Path(second["comparison_path"])
        if not second_path.is_absolute():
            second_path = diff.ROOT / second_path
        assert diff.sha(second_path) == second["comparison_sha256"]
        first_build = build
        second_build = json.loads(second_path.read_text())
        assert first_build["source_sha256"] == second_build["source_sha256"]
        assert first_build["selected_toolchain"] == second_build["selected_toolchain"]
        assert first_build["comparison"]["candidate_sha256"] == second_build["comparison"]["candidate_sha256"]
        assert second_build["build_log_sha256"] == diff.sha(gzip.decompress(
            (second_path.parent / "second-build.log.gz").read_bytes()))
    assert receipt["idl_sha256"] == diff.sha(diff.IDL)
    assert receipt["global_snapshot_sha256"] == diff.sha(diff.SNAPSHOT)
    for path, checksum in receipt["source_sha256"].items():
        assert checksum == diff.sha(diff.ROOT / path), path
    for name, checksum in receipt["dependency_sha256"].items():
        assert checksum == diff.sha(diff.ROOT / "evidence/dependencies" / name / "deployed.so")
    if expected_baseline == "80990317bd9c0363e071646b892490886d7bf946":
        package = build_path.parent
        reproducibility = json.loads((package / "build-reproducibility.json").read_text())
        assert reproducibility["source_base_commit"] == expected_baseline
        assert reproducibility["candidate_sha256"] == receipt["candidate_sha256"]
        assert reproducibility["builds_identical"] and not reproducibility["deployed_byte_match"]
        assert reproducibility["source_sha256"] == build["source_sha256"]
        for filename in ("build-attempt.json", "second-build-attempt.json"):
            attempt = json.loads((package / filename).read_text())
            assert attempt["returncode"] == 0 and attempt["source_unchanged"]
            assert attempt["source_sha256"] == build["source_sha256"]
        regression = json.loads((package / "regression-summary.json").read_text())
        quote_file = package / "quote-control-regression.json.gz"
        curve_file = package / "multi-hop-regression.json.gz"
        quote = json.loads(gzip.decompress(quote_file.read_bytes()))
        curve = json.loads(gzip.decompress(curve_file.read_bytes()))
        assert regression["candidate_sha256"] == receipt["candidate_sha256"]
        assert regression["quote_control"]["receipt_sha256"] == diff.sha(quote_file)
        assert regression["multi_hop_curve"]["receipt_sha256"] == diff.sha(curve_file)
        assert quote["cases"] == 507 and quote["mismatches"] == 0
        assert all(checksum == diff.sha(diff.ROOT / path)
                   for path, checksum in quote["bound_inputs_sha256"].items())
        assert curve["case_count"] == curve["passed"] == 56
        assert curve["candidate_sha256"] == receipt["candidate_sha256"]
    idl = json.loads(diff.IDL.read_text())
    item = next(item for item in idl["instructions"]
                if item["name"] == "admin_update_token_incentives")
    event_disc = bytes(next(event for event in idl["events"]
                            if event["name"] == "AdminUpdateTokenIncentivesEvent")["discriminator"])
    global_fixture = next(row for row in json.loads(diff.SNAPSHOT.read_text())["accounts"]
                          if row["program_name"] == "pump")
    assert global_fixture["data_sha256"] == receipt["global_snapshot_account_data_sha256"]
    assert len(receipt["cases"]) == len(diff.variants()) == receipt["summary"]["cases"] == 98
    successes = 0
    for row, (name, variant) in zip(receipt["cases"], diff.variants()):
        assert row["case"] == name and row["variant"] == variant
        assert row["match"] and not row["differing_fields"]
        for binary, stored in ((diff.TARGET, row["target"]),
                               (candidate_path, row["candidate"])):
            observed = diff.run(binary, item, variant, global_fixture)
            assert observed == stored, (name, binary)
            assert observed["signature_verified"]
        target, candidate = row["target"], row["candidate"]
        for field in ("error", "error_code", "before", "after",
                      "signed_transaction_base64", "signature", "events",
                      "state_debug_logs", "inner_instructions", "return_data_hex",
                      "args", "keys"):
            assert target[field] == candidate[field], (name, field)
        if target["error"] is None:
            successes += 1
            assert len(target["events"]) == 1
            assert len(target["state_debug_logs"]) == 1
            event = base64.b64decode(target["events"][0])
            assert len(event) == 88 and event[:8] == event_disc
            assert event[40:72] == bytes(diff.MINT)
            assert bytes.fromhex(target["inner_instructions"][-1]["data_hex"])[8:] == event
        else:
            assert not target["state_debug_logs"]
            # The wrong self-CPI program errors after emit! wrote its log
            # event; transaction rollback still preserves every account.
            if name == "wrong_program":
                assert len(target["events"]) == 1 and not target["inner_instructions"]
            else:
                assert not target["events"]
            for account in FINANCIAL_ACCOUNTS:
                assert target["before"][account] == target["after"][account], (name, account)
    assert successes == receipt["summary"]["target_successes"] == 43
    assert receipt["summary"]["matched"] == 98
    print(json.dumps({"verified": True, "signed_cases": len(receipt["cases"]),
                      "successes": successes, "rollbacks": len(receipt["cases"]) - successes,
                      "candidate_sha256": receipt["candidate_sha256"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=diff.OUTPUT)
    parser.add_argument("--candidate", type=Path, default=diff.CANDIDATE)
    parser.add_argument("--build-comparison", type=Path, default=diff.BUILD)
    parser.add_argument("--expected-baseline", default="4ffe8bd88761059693e481ae972443c10204f7af")
    args = parser.parse_args()
    main(args.receipt, args.candidate, args.build_comparison, args.expected_baseline)
