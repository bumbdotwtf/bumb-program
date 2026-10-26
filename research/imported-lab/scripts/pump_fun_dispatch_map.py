"""Map official Pump.fun IDL selectors to pinned executable branch/call sites."""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "analysis/pump_fun"
DOCS = ROOT / "third_party/pump-public-docs"
OUTPUT = LANE / "dispatch-map.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_asm(path):
    instructions = {}
    section_offsets = {}
    for line in path.read_text().splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+(.+)", line)
        if not match:
            continue
        address = int(match.group(1), 16)
        instructions[address] = bytes.fromhex(match.group(2))
        label = re.search(r"<\.text\+0x([0-9a-f]+)>", match.group(3))
        if label:
            section_offsets[address] = int(label.group(1), 16)
    return instructions, section_offsets


def main():
    manifest = json.loads((LANE / "program-manifest.json").read_text())
    inventory = json.loads((LANE / "elf-inventory.json").read_text())
    inventory_by_name = {row["name"]: row for row in inventory["programs"]}
    programs = []
    for item in manifest["programs"]:
        name = Path(item["path"]).stem
        path = ROOT / item["path"]
        assert sha(path.read_bytes()) == item["payload_sha256"]
        idl_path = DOCS / "idl" / f"{name}.json"
        assert sha(idl_path.read_bytes()) == item["idl_sha256"]
        idl = json.loads(idl_path.read_text())
        assert idl["address"] == item["program"]
        asm_path = LANE / f"{name}.asm"
        instructions, section_offsets = parse_asm(asm_path)
        inv = inventory_by_name[name]
        rows = []
        failures = []
        for declaration in idl["instructions"]:
            selector = bytes(declaration["discriminator"])
            hits = inv["selector_lddw_hits"][declaration["name"]]
            if len(hits) != 1:
                failures.append((declaration["name"], "selector_hits", len(hits)))
                continue
            compare = int(hits[0], 16)
            encoded = instructions.get(compare, b"")
            if (len(encoded) != 16 or encoded[0] != 0x18 or
                    encoded[4:8] + encoded[12:16] != selector):
                failures.append((declaration["name"], "lddw", hex(compare)))
                continue
            candidates = [(at, instructions.get(at, b""))
                          for at in (compare + 16, compare + 24, compare + 32)]
            branches = [(at, raw) for at, raw in candidates
                        if len(raw) == 8 and raw[:2] == bytes([0x1d, 0x43])
                        and at in section_offsets]
            if len(branches) != 1:
                failures.append((declaration["name"], "branch", [hex(at) for at, _ in branches]))
                continue
            branch_at, branch = branches[0]
            target = branch_at + 8 + 8 * int.from_bytes(
                branch[2:4], "little", signed=True)
            if target not in instructions:
                failures.append((declaration["name"], "target", hex(target)))
                continue
            label_offset = section_offsets.get(branch_at)
            if label_offset is None or target - label_offset != inv["text_virtual_address"]:
                failures.append((declaration["name"], "section_offset", hex(target)))
                continue
            calls = []
            for at in range(target, target + 0x90, 8):
                raw = instructions.get(at, b"")
                if len(raw) != 8:
                    break
                if raw[:2] == bytes([0x85, 0x10]):
                    calls.append((at, raw))
                    break
                if raw[0] in (0x05, 0x95):  # unconditional jump or exit
                    break
            if len(calls) != 1:
                failures.append((declaration["name"], "direct_call", hex(target)))
                continue
            call_at, call = calls[0]
            handler = call_at + 8 + 8 * int.from_bytes(
                call[4:8], "little", signed=True)
            if handler not in instructions:
                failures.append((declaration["name"], "handler", hex(handler)))
                continue
            rows.append({"instruction": declaration["name"],
                         "discriminator_hex": selector.hex(),
                         "compare_at": hex(compare), "branch_at": hex(branch_at),
                         "target_section_offset": hex(label_offset),
                         "branch_target": hex(target),
                         "branch_after_compare_bytes": branch_at - compare,
                         "handler_call_at": hex(call_at),
                         "call_after_target_bytes": call_at - target,
                         "handler_entry": hex(handler)})
        programs.append({"name": name, "program": item["program"],
                         "binary_sha256": item["payload_sha256"],
                         "disassembly_sha256": sha(asm_path.read_bytes()),
                         "text_virtual_address": hex(inv["text_virtual_address"]),
                         "declared_instruction_count": len(idl["instructions"]),
                         "mapped_dispatch_count": len(rows),
                         "distinct_handler_entries": len({r["handler_entry"] for r in rows}),
                         "failures": failures, "instructions": rows})
    OUTPUT.write_text(json.dumps({
        "official_docs_commit": manifest["official_docs_commit"],
        "method": "For each official IDL discriminator, verify one pinned .text lddw immediate, its nearby jeq r3,r4, decode the signed branch offset to a virtual destination, then decode the first direct call in that dispatch block. This maps wrappers only, not account or handler behavior.",
        "programs": programs}, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT), "programs": [{
        "name": row["name"], "mapped": row["mapped_dispatch_count"],
        "declared": row["declared_instruction_count"],
        "distinct_handlers": row["distinct_handler_entries"],
        "failures": row["failures"][:8]} for row in programs]}, indent=2))
    assert all(not row["failures"] and
               row["mapped_dispatch_count"] == row["declared_instruction_count"]
               for row in programs)


if __name__ == "__main__":
    main()
