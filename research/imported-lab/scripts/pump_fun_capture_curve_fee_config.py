"""Read-only finalized Pump fee-config capture for a fresh local curve trade."""

import base64
import hashlib
import json
from datetime import datetime, timezone

from solders.pubkey import Pubkey

from pump_fun_capture import DOCS, PROGRAMS, ROOT, rpc_account


def main():
    pump, fees = PROGRAMS["pump"][0], PROGRAMS["pump_fees"][0]
    idl = json.loads((DOCS / "idl/pump.json").read_text())
    instruction = next(ix for ix in idl["instructions"] if ix["name"] == "buy_v3")
    account = next(a for a in instruction["accounts"] if a["name"] == "fee_config")
    seeds = [bytes(a["value"]) for a in account["pda"]["seeds"]]
    assert seeds == [b"fee_config", bytes(Pubkey.from_string(pump))]
    fee_program = Pubkey.from_bytes(bytes(account["pda"]["program"]["value"]))
    assert str(fee_program) == fees
    address = Pubkey.find_program_address(seeds, fee_program)[0]
    result = rpc_account(str(address))
    value = result["value"]
    assert value["owner"] == fees and not value["executable"]
    raw = base64.b64decode(value["data"][0])
    fee_idl = json.loads((DOCS / "idl/pump_fees.json").read_text())
    definition = next(a for a in fee_idl["accounts"] if a["name"] == "FeeConfig")
    assert raw[:8] == bytes(definition["discriminator"])
    global_capture = next(row for row in json.loads((ROOT / "analysis/pump_fun/config-snapshot.json").read_text())["accounts"]
                          if row["program_name"] == "pump")
    global_data = base64.b64decode(global_capture["data_base64"])
    assert hashlib.sha256(global_data).hexdigest() == global_capture["data_sha256"]
    assert len(global_data) == 1088
    buyback_wallet = Pubkey.from_bytes(global_data[741:773])
    wallet_result = rpc_account(str(buyback_wallet))
    wallet = wallet_result["value"]
    wallet_raw = base64.b64decode(wallet["data"][0])
    out = ROOT / "analysis/pump_fun/curve-fee-config-snapshot.json"
    out.write_text(json.dumps({"captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "commitment": "finalized", "pump_program": pump, "fees_program": fees,
        "fee_config": {"address": str(address), "slot": result["context"]["slot"],
            "owner": value["owner"], "lamports": value["lamports"],
            "data_base64": value["data"][0], "data_sha256": hashlib.sha256(raw).hexdigest(),
            "data_bytes": len(raw)},
        "buyback_wallet": {"address": str(buyback_wallet),
            "slot": wallet_result["context"]["slot"],
            "owner": wallet["owner"], "lamports": wallet["lamports"],
            "data_base64": wallet["data"][0],
            "data_sha256": hashlib.sha256(wallet_raw).hexdigest(),
            "data_bytes": len(wallet_raw)},
        "global_data_sha256": global_capture["data_sha256"],
        "scope": "Read-only finalized fee config and a buyback wallet selected from the captured Pump Global; local buy_v3 may use them without any live transaction."},
        indent=2) + "\n")
    print(json.dumps({"receipt": str(out), "fee_config": str(address),
                      "bytes": len(raw), "buyback_wallet": str(buyback_wallet)}))


if __name__ == "__main__":
    main()
