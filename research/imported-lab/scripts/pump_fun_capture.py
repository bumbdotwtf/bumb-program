"""Read-only finalized capture of the three Pump.fun public-IDL programs.

Only getAccountInfo is used. No wallet, signature, simulation, or transaction
submission is involved. ProgramData payloads are saved verbatim, including
allocated trailing padding, so later local execution pins exact bytes.
"""

import base64
import hashlib
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from solders.pubkey import Pubkey


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "third_party/pump-public-docs"
DOCS_COMMIT = "639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22"
RPC = "https://api.mainnet-beta.solana.com"
PROGRAMS = {
    "pump": ("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
             "7616681ea557975f9f623ac211080f22a93060781eaf4765b0a488d980997207"),
    "pump_amm": ("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
                 "b7d8c57a4d9c4dd0109a9ab893052352333252d4eedced10ac091d4d66cab89b"),
    "pump_fees": ("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ",
                  "6b9fa3eccc6e06273076a47b581f9fcb9e531bb7c3c88acbcd44db55a4002b29"),
}
LOADER = "BPFLoaderUpgradeab1e11111111111111111111111"


def rpc_account(address):
    request = urllib.request.Request(RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": address,
                         "method": "getAccountInfo", "params": [address,
            {"encoding": "base64", "commitment": "finalized"}]}).encode(),
        headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                body = json.load(response)
            if "error" in body:
                raise RuntimeError((address, body["error"]))
            result = body["result"]
            assert result["value"] is not None, address
            return result
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def main():
    assert subprocess.check_output(["git", "-C", str(DOCS), "rev-parse", "HEAD"],
                                   text=True).strip() == DOCS_COMMIT
    staged = []
    for name, (program, idl_hash) in PROGRAMS.items():
        idl_path = DOCS / "idl" / f"{name}.json"
        assert hashlib.sha256(idl_path.read_bytes()).hexdigest() == idl_hash
        idl = json.loads(idl_path.read_text())
        assert idl["address"] == program
        program_result = rpc_account(program)
        program_account = program_result["value"]
        assert program_account["executable"] and program_account["owner"] == LOADER
        program_raw = base64.b64decode(program_account["data"][0])
        assert len(program_raw) == 36
        assert int.from_bytes(program_raw[:4], "little") == 2
        programdata_address = str(Pubkey.from_bytes(program_raw[4:36]))
        programdata_result = rpc_account(programdata_address)
        programdata_account = programdata_result["value"]
        assert not programdata_account["executable"]
        assert programdata_account["owner"] == LOADER
        programdata_raw = base64.b64decode(programdata_account["data"][0])
        assert int.from_bytes(programdata_raw[:4], "little") == 3
        assert programdata_raw[45:49] == b"\x7fELF"
        payload = programdata_raw[45:]
        authority = (str(Pubkey.from_bytes(programdata_raw[13:45]))
                     if programdata_raw[12] else None)
        staged.append((name, payload, {
            "program": program, "programdata": programdata_address,
            "program_account_capture_slot": program_result["context"]["slot"],
            "programdata_capture_slot": programdata_result["context"]["slot"],
            "program_account_raw_sha256": hashlib.sha256(program_raw).hexdigest(),
            "programdata_account_raw_sha256": hashlib.sha256(programdata_raw).hexdigest(),
            "last_deploy_slot": int.from_bytes(programdata_raw[4:12], "little"),
            "upgrade_authority": authority,
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "payload_bytes": len(payload),
            "programdata_raw_bytes": len(programdata_raw),
            "idl_sha256": idl_hash, "idl_instruction_count": len(idl["instructions"]),
            "path": f"inputs/pump_fun/{name}.so"}))
    for name, payload, _ in staged:
        destination = ROOT / "inputs/pump_fun" / f"{name}.so"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
    manifest = {
        "endpoint": RPC, "commitment": "finalized",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_docs_commit": DOCS_COMMIT,
        "programs": [entry for _, _, entry in staged],
        "scope": "Read-only program and ProgramData getAccountInfo responses; payloads retain allocation padding. IDL selector declarations are not yet verified against these executables. No wallet or transaction was used."}
    path = ROOT / "analysis/pump_fun/program-manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(path), "programs": [
        {"program": entry["program"], "last_deploy_slot": entry["last_deploy_slot"],
         "payload_sha256": entry["payload_sha256"], "payload_bytes": entry["payload_bytes"]}
        for _, _, entry in staged]}, indent=2))


if __name__ == "__main__":
    main()
