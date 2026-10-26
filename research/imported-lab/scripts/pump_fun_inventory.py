"""Offline ELF and IDL-selector inventory for the pinned Pump.fun programs."""

import hashlib
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "analysis/pump_fun/program-manifest.json"
DOCS = ROOT / "third_party/pump-public-docs"
OUTPUT = ROOT / "analysis/pump_fun/elf-inventory.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text())
    rows = []
    for item in manifest["programs"]:
        name = Path(item["path"]).stem
        path = ROOT / item["path"]
        blob = path.read_bytes()
        assert sha(blob) == item["payload_sha256"]
        idl_path = DOCS / "idl" / f"{name}.json"
        assert sha(idl_path.read_bytes()) == item["idl_sha256"]
        idl = json.loads(idl_path.read_text())
        assert idl["address"] == item["program"]
        with path.open("rb") as stream:
            elf = ELFFile(stream)
            sections = []
            extent = elf["e_ehsize"]
            for section in elf.iter_sections():
                size = section["sh_size"]
                offset = section["sh_offset"]
                if section["sh_type"] != "SHT_NOBITS":
                    extent = max(extent, offset + size)
                sections.append({"name": section.name, "offset": offset,
                                 "virtual_address": section["sh_addr"],
                                 "size": size,
                                 "sha256": sha(section.data())
                                 if section["sh_type"] != "SHT_NOBITS" else None})
            extent = max(extent, elf["e_shoff"] +
                         elf["e_shentsize"] * elf["e_shnum"])
            for segment in elf.iter_segments():
                extent = max(extent, segment["p_offset"] + segment["p_filesz"])
            text_section = elf.get_section_by_name(".text")
            assert text_section is not None
            code = text_section.data()
            base = text_section["sh_addr"]
            declared = {bytes(ix["discriminator"]): ix["name"]
                        for ix in idl["instructions"]}
            assert len(declared) == len(idl["instructions"])
            selector_hits = {name: [] for name in declared.values()}
            for offset in range(0, len(code) - 15, 8):
                if code[offset] != 0x18:
                    continue
                value = code[offset + 4:offset + 8] + code[offset + 12:offset + 16]
                if value in declared:
                    selector_hits[declared[value]].append(hex(base + offset))
            rows.append({"name": name, "program": item["program"],
                         "payload_sha256": item["payload_sha256"],
                         "payload_bytes": len(blob), "elf_extent_bytes": extent,
                         "allocation_padding_bytes": len(blob) - extent,
                         "allocation_padding_all_zero": not any(blob[extent:]),
                         "machine": str(elf["e_machine"]), "flags": elf["e_flags"],
                         "entrypoint": elf["e_entry"],
                         "text_virtual_address": base,
                         "text_bytes": len(code), "text_sha256": sha(code),
                         "sections": sections,
                         "idl_instruction_count": len(idl["instructions"]),
                         "idl_account_types": [a["name"] for a in idl.get("accounts", [])],
                         "selector_lddw_hit_count": sum(bool(v) for v in selector_hits.values()),
                         "selector_lddw_hits": selector_hits,
                         "unmatched_idl_selectors": [name for name, hits in selector_hits.items()
                                                     if not hits]})
    OUTPUT.write_text(json.dumps({"official_docs_commit": manifest["official_docs_commit"],
        "scope": "Exact pinned ProgramData payload sections and lddw-immediate occurrences of official IDL discriminators in .text. A hit is not a verified dispatcher branch or handler behavior; a miss is not proof of absence.",
        "programs": rows}, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT), "programs": [{
        "name": row["name"], "payload_bytes": row["payload_bytes"],
        "elf_extent_bytes": row["elf_extent_bytes"],
        "text_bytes": row["text_bytes"],
        "selector_hits": row["selector_lddw_hit_count"],
        "idl_instructions": row["idl_instruction_count"]}
        for row in rows]}, indent=2))


if __name__ == "__main__":
    main()
