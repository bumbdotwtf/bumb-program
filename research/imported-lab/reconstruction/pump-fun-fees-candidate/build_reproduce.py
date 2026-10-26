"""Clean-build the incomplete Pump Fees SBF candidate twice and compare it."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CANDIDATE = PACKAGE / "target/deploy/pump_fees_candidate.so"
REFERENCE = ROOT / "inputs/pump_fun/pump_fees.so"
OUT = PACKAGE / "build-reproducibility.json"
COMPARE = ROOT / "analysis/source_reconstruction/pump-fun-fees-candidate-compare.json"
sys.path.insert(0, str(ROOT / "scripts"))
from source_reconstruction_compare import comparison, describe  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True,
                            text=True)
    return (result.stdout + result.stderr).strip()


def main():
    assert sha(REFERENCE) == \
        "4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e"
    source_paths = [PACKAGE / name for name in (
        "Cargo.toml", "Cargo.lock", "generate.py", "src/lib.rs",
        "src/contexts.rs", "src/types.rs")]
    before = {str(path.relative_to(ROOT)): sha(path) for path in source_paths}
    run([sys.executable, str(PACKAGE / "generate.py")])
    assert {str(path.relative_to(ROOT)): sha(path) for path in source_paths} == before
    manifest = str((PACKAGE / "Cargo.toml").relative_to(ROOT))
    clean = ["cargo", "clean", "--manifest-path", manifest]
    build = ["cargo", "build-sbf", "--manifest-path", manifest, "--offline"]
    hashes = []
    for _ in range(2):
        run(clean)
        run(build)
        hashes.append(sha(CANDIDATE))
    assert hashes[0] == hashes[1]
    reference = describe(REFERENCE)
    candidate = describe(CANDIDATE)
    diff = comparison(reference, candidate, REFERENCE, CANDIDATE)
    assert reference["machine"] == candidate["machine"] == "263"
    assert reference["elf_flags"] == candidate["elf_flags"] == 0
    assert not diff["whole_file_equal"] and not diff["elf_bytes_equal"]
    comparison_report = {"target": "pump-fun-fees",
                         "reference": reference,
                         "candidate": candidate,
                         "comparison": diff,
                         "source_reconstruction_status":
                         "IDL-complete fail-closed candidate; behavior and bytes differ"}
    COMPARE.write_text(json.dumps(comparison_report, indent=2) + "\n")
    report = {"scope": "Two clean offline SBF builds of an incomplete 31-handler Pump Fees candidate. The reference binary is a comparison input only; no target bytes are copied or patched into the build. This does not demonstrate source or behavior equivalence.",
              "clean_command": clean, "build_command": build,
              "build_sbf_version": run(["cargo", "build-sbf", "--version"]).splitlines(),
              "source_sha256": before,
              "candidate_clean_build_sha256": hashes,
              "clean_builds_identical": True,
              "reference_sha256": reference["whole_sha256"],
              "candidate_sha256": candidate["whole_sha256"],
              "reference_elf_bytes": reference["elf_bytes"],
              "candidate_elf_bytes": candidate["elf_bytes"],
              "reference_text_bytes": next(s["size"] for s in reference["sections"]
                                           if s["name"] == ".text"),
              "candidate_text_bytes": next(s["size"] for s in candidate["sections"]
                                           if s["name"] == ".text"),
              "same_machine_and_flags": True,
              "same_section_names_and_order": [s["name"] for s in reference["sections"]] ==
                                              [s["name"] for s in candidate["sections"]],
              "whole_program_equal": False,
              "comparison_path": str(COMPARE.relative_to(ROOT))}
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    generated_keypair = PACKAGE / "target/deploy/pump_fees_candidate-keypair.json"
    if generated_keypair.is_file():
        generated_keypair.unlink()
    print(json.dumps({"clean_builds_identical": True,
                      "candidate_elf_bytes": candidate["elf_bytes"],
                      "deployed_elf_bytes": reference["elf_bytes"],
                      "same_machine_and_flags": True,
                      "whole_program_equal": False}))


if __name__ == "__main__":
    main()
