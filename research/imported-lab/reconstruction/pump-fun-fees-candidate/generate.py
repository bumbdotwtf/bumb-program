"""Generate a fail-closed Anchor interface from the pinned official Fees IDL.

This is a research scaffold. IDL account flags are represented; PDA, owner,
mint, ATA, arithmetic, CPI and state-transition bodies are not recovered.
"""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
IDL = ROOT / "third_party/pump-public-docs/idl/pump_fees.json"
EXPECTED_IDL_SHA = "6b9fa3eccc6e06273076a47b581f9fcb9e531bb7c3c88acbcd44db55a4002b29"


def rust_type(spec):
    if isinstance(spec, str):
        if spec == "pubkey":
            return "Pubkey"
        if spec == "string":
            return "String"
        if spec == "bytes":
            return "Vec<u8>"
        assert spec in {"bool", "u8", "u16", "u32", "u64", "u128",
                        "i8", "i16", "i32", "i64", "i128"}, spec
        return spec
    if "option" in spec:
        return f"Option<{rust_type(spec['option'])}>"
    if "vec" in spec:
        return f"Vec<{rust_type(spec['vec'])}>"
    if "array" in spec:
        item, count = spec["array"]
        return f"[{rust_type(item)}; {count}]"
    if "defined" in spec:
        return spec["defined"]["name"]
    raise ValueError(spec)


def pascal(name):
    return "".join(part.title() for part in name.split("_"))


def main():
    assert hashlib.sha256(IDL.read_bytes()).hexdigest() == EXPECTED_IDL_SHA
    idl = json.loads(IDL.read_text())
    assert idl["address"] == "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"
    assert len(idl["instructions"]) == 31
    contexts = ["//! IDL-derived account order/flags only; business constraints are open.",
                "use anchor_lang::prelude::*;", ""]
    handlers = ["//! Fail-closed full-interface candidate for pinned Pump Fees.",
                "//! It is not the deployed program source.",
                "use anchor_lang::prelude::*;", "",
                "mod contexts;", "mod types;",
                "use contexts::*;", "use types::*;", "",
                "declare_id!(\"pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ\");",
                "", "#[program]", "pub mod pump_fees_candidate {",
                "    use super::*;", ""]
    for instruction in idl["instructions"]:
        name = instruction["name"]
        assert re.fullmatch(r"[a-z][a-z0-9_]*", name)
        expected = hashlib.sha256(f"global:{name}".encode()).digest()[:8]
        assert bytes(instruction["discriminator"]) == expected, name
        cls = pascal(name)
        accounts = instruction["accounts"]
        if accounts:
            contexts.extend(["#[derive(Accounts)]", f"pub struct {cls}<'info> {{"])
            for account in accounts:
                field = account["name"]
                assert re.fullmatch(r"[a-z][a-z0-9_]*", field), field
                if account.get("writable"):
                    contexts.append("    #[account(mut)]")
                if account.get("signer"):
                    kind = "Signer<'info>"
                elif field == "system_program":
                    kind = "Program<'info, System>"
                else:
                    contexts.append("    /// CHECK: Exact deployed constraint not recovered.")
                    kind = "UncheckedAccount<'info>"
                contexts.append(f"    pub {field}: {kind},")
            contexts.extend(["}", ""])
        else:
            contexts.extend(["#[derive(Accounts)]", f"pub struct {cls} {{}}", ""])
        args = [f"{arg['name']}: {rust_type(arg['type'])}"
                for arg in instruction["args"]]
        signature = ", ".join([f"_ctx: Context<{cls}>", *args])
        handlers.extend(["    #[allow(unused_variables)]",
                         f"    pub fn {name}({signature}) -> Result<()> {{",
                         "        Err(error!(CandidateError::Unsupported))",
                         "    }", ""])
    handlers.extend(["}", "", "#[error_code]", "pub enum CandidateError {",
                     "    #[msg(\"Research candidate handler not reconstructed\")]",
                     "    Unsupported,", "}", ""])
    types = ["//! IDL argument types needed for instruction deserialization.",
             "use anchor_lang::prelude::*;", ""]
    needed = {"OptionBool", "Fees", "FeeTier", "Shareholder"}
    for entry in idl["types"]:
        name = entry["name"]
        if name not in needed:
            continue
        kind = entry["type"]
        assert kind["kind"] == "struct"
        types.append("#[derive(AnchorSerialize, AnchorDeserialize, Clone)]")
        if name == "OptionBool":
            assert kind["fields"] == ["bool"]
            types.append("pub struct OptionBool(pub bool);")
        else:
            types.append(f"pub struct {name} {{")
            for field in kind["fields"]:
                assert re.fullmatch(r"[a-z][a-z0-9_]*", field["name"])
                types.append(f"    pub {field['name']}: {rust_type(field['type'])},")
            types.append("}")
        types.append("")
    assert {name for name in needed if f"pub struct {name}" in "\n".join(types)} == needed
    source = PACKAGE / "src"
    source.mkdir(parents=True, exist_ok=True)
    for filename, lines in (("contexts.rs", contexts), ("lib.rs", handlers),
                            ("types.rs", types)):
        (source / filename).write_text("\n".join(lines).rstrip("\n") + "\n")
    print(f"generated {len(idl['instructions'])} fail-closed handlers and contexts")


if __name__ == "__main__":
    main()
