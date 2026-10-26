"""Read-only finalized capture of one canonical config per Pump.fun program."""

import base64
import hashlib
import json
from datetime import datetime, timezone

from solders.pubkey import Pubkey

from pump_fun_capture import DOCS, PROGRAMS, ROOT, rpc_account


SELECTED = {
    "pump": ("set_max_curve_depth", "global", "Global", b"global"),
    "pump_amm": ("disable", "global_config", "GlobalConfig", b"global_config"),
    "pump_fees": ("set_claim_rate_limit", "fee_program_global",
                  "FeeProgramGlobal", b"fee-program-global"),
}


def main():
    rows = []
    for name, (instruction, account_name, account_type, seed) in SELECTED.items():
        program = PROGRAMS[name][0]
        idl = json.loads((DOCS / "idl" / f"{name}.json").read_text())
        declaration = next(ix for ix in idl["instructions"]
                           if ix["name"] == instruction)
        account = next(a for a in declaration["accounts"]
                       if a["name"] == account_name)
        if "pda" in account:
            assert len(account["pda"]["seeds"]) == 1
            assert bytes(account["pda"]["seeds"][0]["value"]) == seed
        else:
            # `disable` names GlobalConfig without restating its PDA in the
            # instruction IDL; the official PumpSwap docs give this seed.
            assert name == "pump_amm" and account_name == "global_config"
        address, bump = Pubkey.find_program_address(
            [seed], Pubkey.from_string(program))
        if name == "pump_amm":
            assert str(address) == "ADyA8hdefvWN2dbGGWFotbzWxrAvLW83WG6QCVXvJKqw"
        result = rpc_account(str(address))
        value = result["value"]
        assert value["owner"] == program and not value["executable"]
        data = base64.b64decode(value["data"][0])
        account_declaration = next(a for a in idl["accounts"]
                                   if a["name"] == account_type)
        assert data[:8] == bytes(account_declaration["discriminator"])
        rows.append({"program_name": name, "program": program,
                     "selected_instruction": instruction,
                     "config_account_type": account_type,
                     "pda_seed_hex": seed.hex(), "pda_bump": bump,
                     "address": str(address), "capture_slot": result["context"]["slot"],
                     "lamports": value["lamports"], "owner": value["owner"],
                     "data_base64": value["data"][0],
                     "data_sha256": hashlib.sha256(data).hexdigest(),
                     "data_bytes": len(data)})
    output = ROOT / "analysis/pump_fun/config-snapshot.json"
    output.write_text(json.dumps({"captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "commitment": "finalized", "accounts": rows,
        "scope": "Read-only canonical config PDA getAccountInfo captures for later offline signer-substitution tests. No public transaction or wallet is used."},
        indent=2) + "\n")
    print(json.dumps({"output": str(output), "accounts": [{
        "program_name": row["program_name"], "address": row["address"],
        "capture_slot": row["capture_slot"], "bytes": row["data_bytes"],
        "sha256": row["data_sha256"]} for row in rows]}, indent=2))


if __name__ == "__main__":
    main()
