"""Pin ELF/layout baselines and compare source-built candidates without patching bytes.

Usage:
  .venv/bin/python scripts/source_reconstruction_compare.py --target meteora
  .venv/bin/python scripts/source_reconstruction_compare.py --target humidifi
  .venv/bin/python scripts/source_reconstruction_compare.py --target shaw-dao \
      --candidate third_party/daosfun-source/binaries/dao_v1.deployed.so

A match of the published Shaw artifact is a comparator control, not proof that
this lab independently rebuilt its Rust sources. The other targets have no
source-built candidate yet.
"""
import argparse
import hashlib
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "meteora": (
        ROOT / "inputs/meteora/mainnet.so",
        "d296c6771cec945601027613ca637c1be6721044c5859009d41c453477844c1f",
    ),
    "humidifi": (
        ROOT / "inputs/humidifi/mainnet.so",
        "47b5937d5b1f47763503ca0337f998b2c7e6a5b029b19112b9520e5c187a23af",
    ),
    "shaw-dao": (
        ROOT / "third_party/daosfun-source/evidence/mainnet.so",
        "5020271255ea678fc110fed4671a86b1b7268acad04f990c590decd92091143d",
    ),
    "daos-fee-share": (
        ROOT / "inputs/daos_fun/fee_share_trader_dao-mainnet.so",
        "88df1b4ddb152d4159b41b9eba68ab74e6f0e14c1930bad5828c44a14a3ca4f8",
    ),
    "daos-founder": (
        ROOT / "inputs/daos_fun/founder_dao-mainnet.so",
        "816bc6d42ffea7d63bd7b1287589413aef04d8f7dceb34dd274a0f7872d40aa2",
    ),
    "daos-pump": (
        ROOT / "inputs/daos_fun/pump_xyk-mainnet.so",
        "2238aa5b96fc29e7693174b20d75063df2e1dfba28c26c5346338c23732e2fb9",
    ),
    "daos-virtual": (
        ROOT / "inputs/daos_fun/virtual_xyk-mainnet.so",
        "c151c6b15b84d8bfc47a5f2e0e5b9e04babff0263a1125a9e8dcb07df6144377",
    ),
    "pump-fun-pump": (
        ROOT / "inputs/pump_fun/pump.so",
        "7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d",
    ),
    "pump-fun-amm": (
        ROOT / "inputs/pump_fun/pump_amm.so",
        "6a7ad34596d83b4c435b32f458a56e718e9f82eb4ad38e4316616d15d24d8ff7",
    ),
    "pump-fun-fees": (
        ROOT / "inputs/pump_fun/pump_fees.so",
        "4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e",
    ),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def describe(path):
    raw = path.read_bytes()
    with path.open("rb") as handle:
        elf = ELFFile(handle)
        header = elf.header
        extent = header.e_shoff + header.e_shentsize * header.e_shnum
        assert 0 < extent <= len(raw), (path, extent, len(raw))
        sections = []
        for section in elf.iter_sections():
            info = section.header
            file_backed = info.sh_type != "SHT_NOBITS" and info.sh_size > 0
            sections.append({
                "name": section.name,
                "type": str(info.sh_type),
                "file_offset": info.sh_offset,
                "virtual_address": info.sh_addr,
                "size": info.sh_size,
                "alignment": info.sh_addralign,
                "sha256": digest(section.data()) if file_backed else None,
            })
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "whole_sha256": digest(raw),
        "whole_bytes": len(raw),
        "machine": str(header.e_machine),
        "elf_flags": header.e_flags,
        "entry_point": header.e_entry,
        "elf_bytes": extent,
        "elf_sha256": digest(raw[:extent]),
        "allocation_padding_bytes": len(raw) - extent,
        "allocation_padding_all_zero": not any(raw[extent:]),
        "sections": sections,
    }


def comparison(reference, candidate, reference_path, candidate_path):
    ref_bytes = reference_path.read_bytes()
    candidate_bytes = candidate_path.read_bytes()
    first_difference = next(
        (i for i, (a, b) in enumerate(zip(ref_bytes, candidate_bytes)) if a != b),
        None,
    )
    if first_difference is None and len(ref_bytes) != len(candidate_bytes):
        first_difference = min(len(ref_bytes), len(candidate_bytes))
    ref_sections = reference["sections"]
    candidate_sections = candidate["sections"]
    section_rows = []
    for i in range(max(len(ref_sections), len(candidate_sections))):
        a = ref_sections[i] if i < len(ref_sections) else None
        b = candidate_sections[i] if i < len(candidate_sections) else None
        section_rows.append({
            "index": i,
            "reference_name": a["name"] if a else None,
            "candidate_name": b["name"] if b else None,
            "layout_equal": bool(a and b and all(
                a[key] == b[key]
                for key in ("name", "type", "file_offset", "virtual_address", "size", "alignment")
            )),
            "contents_equal": bool(a and b and a["sha256"] == b["sha256"]),
        })
    return {
        "whole_file_equal": ref_bytes == candidate_bytes,
        "elf_extent_equal": reference["elf_bytes"] == candidate["elf_bytes"],
        "elf_bytes_equal": (
            reference["elf_bytes"] == candidate["elf_bytes"]
            and ref_bytes[:reference["elf_bytes"]] == candidate_bytes[:candidate["elf_bytes"]]
        ),
        "padding_equal": (
            ref_bytes[reference["elf_bytes"]:] == candidate_bytes[candidate["elf_bytes"]:]
        ),
        "first_whole_file_difference_offset": first_difference,
        "section_comparison": section_rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    reference_path, expected_sha = TARGETS[args.target]
    reference = describe(reference_path)
    assert reference["whole_sha256"] == expected_sha
    report = {
        "target": args.target,
        "reference": reference,
        "source_reconstruction_status": "no candidate supplied",
    }
    if args.candidate:
        candidate_path = args.candidate.resolve()
        candidate = describe(candidate_path)
        report["candidate"] = candidate
        report["comparison"] = comparison(reference, candidate, reference_path, candidate_path)
        report["source_reconstruction_status"] = (
            "published Shaw artifact comparator control" if args.target == "shaw-dao"
            else "candidate byte comparison only; build provenance must be verified separately"
        )
    output = args.output or ROOT / "analysis/source_reconstruction" / f"{args.target}-baseline.json"
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "target": args.target,
        "elf_bytes": reference["elf_bytes"],
        "padding_bytes": reference["allocation_padding_bytes"],
        "whole_file_equal": report.get("comparison", {}).get("whole_file_equal"),
        "output": str(output),
    }))


if __name__ == "__main__":
    main()
