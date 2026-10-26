"""Read-only finalized PumpSwap pool/fee/vault snapshot for local v2 trade work."""

import base64
import hashlib
import json
import struct
from datetime import datetime, timezone

from solders.pubkey import Pubkey

from pump_fun_capture import DOCS, PROGRAMS, ROOT, rpc_account


POOL = "GseMAnNDvntR5uFePZ51yZBXzNSn7GdFPkfHwfr6d77J"
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")


def captured(address):
    result = rpc_account(str(address))
    row = result["value"]
    return {"address": str(address), "slot": result["context"]["slot"],
            "lamports": row["lamports"], "owner": row["owner"],
            "executable": row["executable"], "data_base64": row["data"][0],
            "data_sha256": hashlib.sha256(base64.b64decode(row["data"][0])).hexdigest()}


def raw(row):
    return base64.b64decode(row["data_base64"])


def main():
    amm = PROGRAMS["pump_amm"][0]
    fees = PROGRAMS["pump_fees"][0]
    idl = json.loads((DOCS / "idl/pump_amm.json").read_text())
    pool_row = captured(POOL)
    pool = raw(pool_row)
    account = next(a for a in idl["accounts"] if a["name"] == "Pool")
    assert pool_row["owner"] == amm and pool[:8] == bytes(account["discriminator"])
    assert len(pool) >= 211
    keys = {"base_mint": str(Pubkey.from_bytes(pool[43:75])),
            "quote_mint": str(Pubkey.from_bytes(pool[75:107])),
            "pool_base_token_account": str(Pubkey.from_bytes(pool[139:171])),
            "pool_quote_token_account": str(Pubkey.from_bytes(pool[171:203]))}
    assert keys["quote_mint"] == "So11111111111111111111111111111111111111112"
    fee_account = next(a for ix in idl["instructions"] if ix["name"] == "buy_v2"
                       for a in ix["accounts"] if a["name"] == "fee_config")
    seeds = [bytes(seed["value"]) for seed in fee_account["pda"]["seeds"]]
    fee_program = Pubkey.from_bytes(bytes(fee_account["pda"]["program"]["value"]))
    assert str(fee_program) == fees
    fee_address = Pubkey.find_program_address(seeds, fee_program)[0]
    keys["fee_config"] = str(fee_address)
    all_rows = {"pool": pool_row}
    for name, address in keys.items():
        all_rows[name] = captured(address)
    assert all_rows["fee_config"]["owner"] == fees
    for name, mint in (("pool_base_token_account", keys["base_mint"]),
                       ("pool_quote_token_account", keys["quote_mint"])):
        account = all_rows[name]
        data = raw(account)
        assert account["owner"] == str(TOKEN)
        assert str(Pubkey.from_bytes(data[:32])) == mint
        assert str(Pubkey.from_bytes(data[32:64])) == POOL
    config = next(row for row in json.loads((ROOT / "analysis/pump_fun/config-snapshot.json").read_text())["accounts"]
                  if row["program_name"] == "pump_amm")
    config_data = base64.b64decode(config["data_base64"])
    assert len(config_data) == 949
    # The first recipient array at offset 57 is for protocol fees. The
    # separate buyback recipient array follows at offset 643 in this IDL.
    recipients = [Pubkey.from_bytes(config_data[643 + 32*i:643 + 32*(i+1)])
                  for i in range(8)]
    selected = None
    for owner in recipients:
        address = Pubkey.find_program_address(
            [bytes(owner), bytes(TOKEN), bytes(Pubkey.from_string(keys["quote_mint"]))], ATA)[0]
        try:
            candidate = captured(address)
        except AssertionError:
            continue
        if candidate["owner"] == str(TOKEN) and str(Pubkey.from_bytes(raw(candidate)[:32])) == keys["quote_mint"]:
            selected = {"wallet": str(owner), "token_account": candidate}
            break
    assert selected is not None, "No captured buyback WSOL ATA among configured wallets"
    all_rows["buyback_fee_recipient"] = selected["token_account"]
    output = ROOT / "analysis/pump_fun/amm-v2-trade-fixture.json"
    output.write_text(json.dumps({"captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "commitment": "finalized", "pool": POOL, "keys": keys,
        "fee_config_seed_hex": [seed.hex() for seed in seeds],
        "buyback_wallet": selected["wallet"], "accounts": all_rows,
        "pool_account_data_bytes": len(pool),
        "pool_lp_supply_raw": struct.unpack_from("<Q", pool, 203)[0],
        "pool_base_vault_amount_raw": struct.unpack_from("<Q", raw(all_rows["pool_base_token_account"]), 64)[0],
        "pool_quote_vault_amount_raw": struct.unpack_from("<Q", raw(all_rows["pool_quote_token_account"]), 64)[0],
        "scope": "Read-only finalized snapshots from an example pool in official PumpSwap docs. They are later account state, not an archival pre-trade state or proof that a v2 trade can execute."},
        indent=2) + "\n")
    print(json.dumps({"output": str(output), "pool": POOL,
        "base_mint": keys["base_mint"], "quote_mint": keys["quote_mint"],
        "base_vault_raw": struct.unpack_from("<Q", raw(all_rows["pool_base_token_account"]), 64)[0],
        "quote_vault_raw": struct.unpack_from("<Q", raw(all_rows["pool_quote_token_account"]), 64)[0],
        "fee_config": str(fee_address),
        "buyback_fee_recipient": selected["token_account"]["address"]}, indent=2))


if __name__ == "__main__":
    main()
