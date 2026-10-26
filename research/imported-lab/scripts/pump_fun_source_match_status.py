"""Reconcile pinned Pump programs against actual source-build candidates."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/source_reconstruction/pump-fun-source-match-status.json"
MANIFEST = ROOT / "analysis/pump_fun/program-manifest.json"
LANE = ROOT / "analysis/source_reconstruction"
PACKAGE = ROOT / "reconstruction/pump-fun-fees-candidate"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text())
    build = json.loads((PACKAGE / "build-reproducibility.json").read_text())
    interface = json.loads((PACKAGE / "interface-verification.json").read_text())
    comparison = json.loads((LANE / "pump-fun-fees-candidate-compare.json").read_text())
    candidate = PACKAGE / "target/deploy/pump_fees_candidate.so"
    assert sha(candidate) == build["candidate_sha256"] == \
           interface["candidate_sha256"] == comparison["candidate"]["whole_sha256"]
    assert build["clean_builds_identical"] and \
           len(set(build["candidate_clean_build_sha256"])) == 1
    assert interface["selector_count"] == interface["unsupported_reached"] == 31
    assert not comparison["comparison"]["whole_file_equal"]
    assert build["same_machine_and_flags"]
    for source, expected in build["source_sha256"].items():
        assert sha(ROOT / source) == expected
    rows = []
    for item in manifest["programs"]:
        name = Path(item["path"]).stem
        slug = {"pump": "pump", "pump_amm": "amm", "pump_fees": "fees"}[name]
        reference_path = LANE / f"pump-fun-{slug}-baseline.json"
        reference = json.loads(reference_path.read_text())
        assert sha(ROOT / item["path"]) == item["payload_sha256"]
        assert reference["reference"]["whole_sha256"] == item["payload_sha256"]
        assert reference["reference"]["whole_bytes"] == item["payload_bytes"]
        row = {"program": item["program"], "name": name,
               "deployed_payload_sha256": item["payload_sha256"],
               "deployed_elf_bytes": reference["reference"]["elf_bytes"],
               "deployed_padding_bytes": reference["reference"]["allocation_padding_bytes"],
               "official_idl_instructions": item["idl_instruction_count"],
               "complete_source_candidate": False,
               "byte_identical_source_rebuild": False,
               "reference_receipt": str(reference_path.relative_to(ROOT))}
        if name == "pump_fees":
            row.update({"incomplete_candidate": "reconstruction/pump-fun-fees-candidate",
                        "candidate_sha256": build["candidate_sha256"],
                        "candidate_elf_bytes": build["candidate_elf_bytes"],
                        "candidate_handlers_dispatched": interface["selector_count"],
                        "candidate_handlers_intentionally_unsupported": interface["unsupported_reached"],
                        "candidate_build_receipt": "reconstruction/pump-fun-fees-candidate/build-reproducibility.json",
                        "candidate_comparison_receipt": "analysis/source_reconstruction/pump-fun-fees-candidate-compare.json"})
        rows.append(row)
    assert len(rows) == 3
    report = {"official_docs_commit": manifest["official_docs_commit"],
              "scope": "Offline source-build status against three pinned finalized Pump.fun ProgramData payloads. The Fees candidate has only IDL-derived interface code and fail-closed bodies. This is not evidence that current source is fully reversed or that any live program is safe.",
              "programs": rows,
              "summary": {"deployed_programs": 3,
                          "idl_selectors_total": sum(row["official_idl_instructions"] for row in rows),
                          "incomplete_whole_interface_candidates": 1,
                          "complete_source_candidates": 0,
                          "byte_identical_source_rebuilds": 0}}
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"]))


if __name__ == "__main__":
    main()
