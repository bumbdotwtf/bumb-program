"""Signed, writable OFFLINE Surfpool smoke paths for three pinned Pump.fun ELFs.

Admin keys in copied configuration accounts are replaced with disposable local
keys. This validates binary execution and account guards, not live key control.
"""

import base64
import hashlib
import json
import struct
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/pump_fun/admin-signed-surfpool.json"
PORT = 19831
RPC = f"http://127.0.0.1:{PORT}"
LOADER = "BPFLoader2111111111111111111111111111111111"
SYSTEM = "11111111111111111111111111111111"
PAYER = Keypair.from_seed(bytes([201]) * 32)
OUTSIDER = Keypair.from_seed(bytes([202]) * 32)
EVENT_SEED = b"__event_authority"
SELECTED = {
    "pump": ("set_max_curve_depth", 9, bytes([1])),
    "pump_amm": ("disable", 8, bytes([0, 0, 0, 1, 0])),
    "pump_fees": ("set_claim_rate_limit", 9, struct.pack("<Q", 600)),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rpc(method, params=None):
    assert method in {"getHealth", "getLatestBlockhash", "getAccountInfo",
                      "getSignatureStatuses", "surfnet_setAccount",
                      "simulateTransaction", "sendTransaction"}
    request = urllib.request.Request(RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                         "params": params or []}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.load(response)
    if "error" in body:
        raise RuntimeError((method, body["error"]))
    return body["result"]


def set_account(address, lamports, data, owner, executable=False):
    rpc("surfnet_setAccount", [str(address), {
        "lamports": lamports, "owner": str(owner), "executable": executable,
        "data": data.hex()}])


def account(address):
    row = rpc("getAccountInfo", [str(address), {"encoding": "base64"}])["value"]
    assert row is not None, address
    return {"lamports": row["lamports"], "owner": row["owner"],
            "data": base64.b64decode(row["data"][0])}


def snapshot(addresses):
    return {name: {"lamports": row["lamports"], "owner": row["owner"],
                   "data_sha256": sha(row["data"]),
                   "data_base64": base64.b64encode(row["data"]).decode()}
            for name, address in addresses.items() if (row := account(address))}


def send(label, instruction, payer, watched, expected_success):
    blockhash = Hash.from_string(rpc("getLatestBlockhash")["value"]["blockhash"])
    tx = Transaction.new_signed_with_payer([instruction], payer.pubkey(),
                                            [payer], blockhash)
    assert all(tx.verify_with_results())
    encoded = base64.b64encode(bytes(tx)).decode()
    before = snapshot(watched)
    payer_before = account(payer.pubkey())["lamports"]
    simulation = rpc("simulateTransaction", [encoded, {"encoding": "base64",
        "sigVerify": True}])["value"]
    assert (simulation["err"] is None) == expected_success, (
        label, simulation["err"], (simulation.get("logs") or [])[-12:])
    signature = rpc("sendTransaction", [encoded, {"encoding": "base64",
        "skipPreflight": not expected_success}])
    status = None
    for _ in range(100):
        status = rpc("getSignatureStatuses", [[signature]])["value"][0]
        if status is not None:
            break
        time.sleep(.05)
    assert status is not None and status["err"] == simulation["err"], label
    after = snapshot(watched)
    if not expected_success:
        assert before == after, label
    payer_after = account(payer.pubkey())["lamports"]
    assert payer_before - payer_after == 5000, (label, payer_before, payer_after)
    return {"label": label, "signature": signature,
            "transaction_base64": encoded,
            "signature_verified": True, "simulation_error": simulation["err"],
            "committed_error": status["err"],
            "units_consumed": simulation.get("unitsConsumed"),
            "payer_fee_lamports": payer_before - payer_after,
            "before": before, "after": after,
            "log_tail": (simulation.get("logs") or [])[-12:]}


def main():
    manifest = json.loads((ROOT / "analysis/pump_fun/program-manifest.json").read_text())
    inventory = {item["name"]: item for item in json.loads(
        (ROOT / "analysis/pump_fun/elf-inventory.json").read_text())["programs"]}
    captured = {row["program_name"]: row for row in json.loads(
        (ROOT / "analysis/pump_fun/config-snapshot.json").read_text())["accounts"]}
    declarations = {}
    for item in manifest["programs"]:
        name = Path(item["path"]).stem
        idl = json.loads((ROOT / "third_party/pump-public-docs/idl" /
                          f"{name}.json").read_text())
        assert idl["address"] == item["program"]
        selected, authority_offset, arguments = SELECTED[name]
        instruction = next(ix for ix in idl["instructions"]
                           if ix["name"] == selected)
        config = captured[name]
        raw = base64.b64decode(config["data_base64"])
        assert sha(raw) == config["data_sha256"]
        assert raw[authority_offset:authority_offset + 32] != bytes(PAYER.pubkey())
        declarations[name] = {"program": Pubkey.from_string(item["program"]),
            "payload": (ROOT / item["path"]).read_bytes(),
            "payload_sha256": item["payload_sha256"],
            "elf_extent": inventory[name]["elf_extent_bytes"],
            "config_address": Pubkey.from_string(config["address"]),
            "config_raw": raw, "config_lamports": config["lamports"],
            "authority_offset": authority_offset,
            "selected": selected, "instruction": instruction,
            "argument_bytes": arguments,
            "event_authority": Pubkey.find_program_address(
                [EVENT_SEED], Pubkey.from_string(item["program"]))[0]}

    process = subprocess.Popen([str(ROOT / "tools/surfpool"), "start",
        "--offline", "--no-deploy", "--no-tui", "--no-studio",
        "--airdrop-amount", "0", "--port", str(PORT), "--ws-port",
        str(PORT + 1), "--db", ":memory:", "--log-level", "error"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(150):
            if process.poll() is not None:
                raise RuntimeError(process.stderr.read().decode()[-1000:])
            try:
                rpc("getHealth")
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(.1)
        else:
            raise TimeoutError("offline Surfpool did not start")
        set_account(PAYER.pubkey(), 10**12, b"", SYSTEM)
        set_account(OUTSIDER.pubkey(), 10**12, b"", SYSTEM)
        for row in declarations.values():
            assert sha(row["payload"]) == row["payload_sha256"]
            set_account(row["program"], 10**10, row["payload"][:row["elf_extent"]],
                        LOADER, True)
            copied = bytearray(row["config_raw"])
            at = row["authority_offset"]
            copied[at:at + 32] = bytes(PAYER.pubkey())
            set_account(row["config_address"], row["config_lamports"],
                        copied, row["program"])
        watched = {name: row["config_address"] for name, row in declarations.items()}
        cases = []
        for name, row in declarations.items():
            ix = row["instruction"]
            metas = []
            for acc in ix["accounts"]:
                account_name = acc["name"]
                if account_name in ("global", "global_config", "fee_program_global"):
                    key = row["config_address"]
                elif account_name in ("authority", "admin"):
                    key = OUTSIDER.pubkey()
                elif account_name == "event_authority":
                    key = row["event_authority"]
                elif account_name == "program":
                    key = row["program"]
                else:
                    raise ValueError((name, account_name))
                metas.append(AccountMeta(key, bool(acc.get("signer")),
                                         bool(acc.get("writable"))))
            data = bytes(ix["discriminator"]) + row["argument_bytes"]
            rejected = send(name + "_wrong_authority", Instruction(row["program"],
                data, metas), OUTSIDER, watched, False)
            cases.append(rejected)
            valid_metas = [AccountMeta(PAYER.pubkey() if meta.pubkey == OUTSIDER.pubkey()
                else meta.pubkey, meta.is_signer, meta.is_writable) for meta in metas]
            accepted = send(name + "_authorized_write", Instruction(row["program"],
                data, valid_metas), PAYER, watched, True)
            cases.append(accepted)
            before_data = base64.b64decode(accepted["before"][name]["data_base64"])
            after_data = base64.b64decode(accepted["after"][name]["data_base64"])
            changed = [i for i, (a, b) in enumerate(zip(before_data, after_data))
                       if a != b]
            assert len(before_data) == len(after_data) and changed, (name, changed)
            if name == "pump":
                assert after_data[-1] == 1 and changed == [len(after_data) - 1]
            elif name == "pump_amm":
                assert after_data[56] == 8 and changed == [56]
            else:
                assert struct.unpack_from("<Q", after_data, 74)[0] == 600
                assert set(changed).issubset(set(range(74, 82)))
            accepted["changed_config_offsets"] = changed
        OUT.write_text(json.dumps({"environment": "offline Surfpool :memory: loopback",
            "programs": {name: {"program": str(row["program"]),
                "payload_sha256": row["payload_sha256"],
                "loaded_elf_extent": row["elf_extent"],
                "captured_config_sha256": sha(row["config_raw"]),
                "config_address": str(row["config_address"]),
                "synthetic_authority": str(PAYER.pubkey()),
                "selected_instruction": row["selected"]}
                for name, row in declarations.items()},
            "cases": cases,
            "qualification": "All six transactions are signed and committed only in isolated offline Surfpool. Pinned current ProgramData payloads are loaded through their exact ELF extents without trailing zero allocation padding. Captured configuration accounts are copied with authority/admin changed to disposable local keys before the first transaction. This proves three bounded signed writes and wrong-authority rollbacks, not access to real authority keys, live governance behavior, trade safety, or full handler reversal. No public RPC or mainnet transaction."},
            indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT), "cases": len(cases),
                          "successful_writes": [x["label"] for x in cases
                                               if x["committed_error"] is None]}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
