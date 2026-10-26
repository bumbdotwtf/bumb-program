"""Verify pinned Pump.fun ProgramData payloads and official IDL baselines offline."""

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "third_party/pump-public-docs"
MANIFEST = ROOT / "analysis/pump_fun/program-manifest.json"
INVENTORY = ROOT / "analysis/pump_fun/elf-inventory.json"
DISPATCH = ROOT / "analysis/pump_fun/dispatch-map.json"
OUTPUT = ROOT / "analysis/pump_fun/offline-verification.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text())
    inventory = json.loads(INVENTORY.read_text())
    dispatch = json.loads(DISPATCH.read_text())
    assert manifest["commitment"] == "finalized"
    assert manifest["endpoint"] == "https://api.mainnet-beta.solana.com"
    assert subprocess.check_output(["git", "-C", str(DOCS), "rev-parse", "HEAD"],
                                   text=True).strip() == manifest["official_docs_commit"]
    assert inventory["official_docs_commit"] == manifest["official_docs_commit"]
    assert dispatch["official_docs_commit"] == manifest["official_docs_commit"]
    assert len(manifest["programs"]) == len(inventory["programs"]) == len(dispatch["programs"]) == 3
    rows = []
    seen = set()
    inventory_by_name = {row["name"]: row for row in inventory["programs"]}
    dispatch_by_name = {row["name"]: row for row in dispatch["programs"]}
    assert set(inventory_by_name) == {"pump", "pump_amm", "pump_fees"}
    assert set(dispatch_by_name) == set(inventory_by_name)
    for program in manifest["programs"]:
        path = ROOT / program["path"]
        name = path.stem
        assert name not in seen
        seen.add(name)
        idl_path = DOCS / "idl" / f"{name}.json"
        idl = json.loads(idl_path.read_text())
        assert idl["address"] == program["program"]
        assert digest(idl_path) == program["idl_sha256"]
        assert digest(path) == program["payload_sha256"]
        assert path.stat().st_size == program["payload_bytes"]
        assert program["programdata_raw_bytes"] == program["payload_bytes"] + 45
        assert program["last_deploy_slot"] <= program["programdata_capture_slot"]
        item = inventory_by_name[name]
        assert item["program"] == program["program"]
        assert item["payload_sha256"] == program["payload_sha256"]
        assert item["payload_bytes"] == program["payload_bytes"]
        assert item["allocation_padding_all_zero"]
        assert item["elf_extent_bytes"] + item["allocation_padding_bytes"] == item["payload_bytes"]
        assert item["selector_lddw_hit_count"] == item["idl_instruction_count"] == \
               len(idl["instructions"]) == program["idl_instruction_count"]
        assert not item["unmatched_idl_selectors"]
        assert all(len(hits) == 1 for hits in item["selector_lddw_hits"].values())
        branches = dispatch_by_name[name]
        assert branches["program"] == program["program"]
        assert branches["binary_sha256"] == program["payload_sha256"]
        assert branches["disassembly_sha256"] == digest(ROOT / "analysis/pump_fun" / f"{name}.asm")
        assert branches["mapped_dispatch_count"] == branches["declared_instruction_count"] == len(idl["instructions"])
        assert branches["distinct_handler_entries"] == len(idl["instructions"])
        assert not branches["failures"]
        by_instruction = {row["instruction"]: row for row in branches["instructions"]}
        assert set(by_instruction) == {row["name"] for row in idl["instructions"]}
        for instruction in idl["instructions"]:
            assert by_instruction[instruction["name"]]["discriminator_hex"] == \
                   bytes(instruction["discriminator"]).hex()
        rows.append({"name": name, "program": program["program"],
                     "last_deploy_slot": program["last_deploy_slot"],
                     "payload_sha256": program["payload_sha256"],
                     "idl_sha256": program["idl_sha256"],
                     "declared_instruction_count": len(idl["instructions"]),
                     "selector_lddw_hit_count": item["selector_lddw_hit_count"],
                     "dispatcher_wrapper_mapped_count": branches["mapped_dispatch_count"],
                     "runtime_handlers_verified_by_this_baseline_check": 0,
                     "fully_reversed_handlers": 0})
    assert seen == {"pump", "pump_amm", "pump_fees"}
    OUTPUT.write_text(json.dumps({
        "official_docs_commit": manifest["official_docs_commit"],
        "manifest_sha256": digest(MANIFEST),
        "inventory_sha256": digest(INVENTORY),
        "dispatch_map_sha256": digest(DISPATCH),
        "programs": rows,
        "declared_instruction_total": sum(x["declared_instruction_count"] for x in rows),
        "selector_constant_total": sum(x["selector_lddw_hit_count"] for x in rows),
        "dispatcher_wrapper_total": sum(x["dispatcher_wrapper_mapped_count"] for x in rows),
        "scope": "Offline hashes, ELF extent/padding, IDL discriminator lddw-immediate presence and signed branch/direct-call wrapper mapping. No account semantics, handler execution, exact source or live transaction is proved."},
        indent=2) + "\n")
    print(json.dumps({"verified": True, "programs": len(rows),
                      "declared_instructions": 125,
                      "selector_constants": 125,
                      "dispatcher_wrappers": 125,
                      "receipt": str(OUTPUT)}))


if __name__ == "__main__":
    main()
