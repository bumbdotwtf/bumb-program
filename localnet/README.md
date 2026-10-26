# Surfpool fixtures and transaction tests

Use **Surfpool 1.6.1** for this project's fixture suite. The earlier 1.0.0 launcher
was tested only for basic program loading; it is superseded by this pinned setup.

## Install once

On macOS ARM64, from the repository root:

```sh
python3.12 localnet/setup.py
```

This installs the SHA-256-verified upstream Surfpool archive into `work/localnet/`,
creates an isolated Python environment with the repository's pinned dependencies,
and checks out the exact official-docs commit used by the fixtures. It does not
change global wallets, CLI settings or installed tools. Python 3.12 is recommended:
the host's Homebrew 3.14 has a broken libexpat linkage affecting pip/ensurepip.
`--python /path/to/python` selects another interpreter for the test environment.

The pinned archive provenance is in
[`tool-downloads.json`](../research/imported-lab/evidence/tool-downloads.json).
Other platforms can supply their installed Surfpool 1.6.1 and docs checkout using
the test runner's `--surfpool` and `--docs-checkout` options.

## Start an interactive fixture network

```sh
python3 localnet/surfpool.py
```

- RPC: `http://127.0.0.1:18999`
- WebSocket: `ws://127.0.0.1:19000`
- Studio: `http://127.0.0.1:18488`
- Stop: Ctrl-C in the launch terminal.

The launcher loads the four captured original programs, five captured dependencies,
and ten captured configuration/pool accounts. Every payload hash is checked before
loading, and every loaded ELF and account is read back and compared. Captured pool
fixtures include mint accounts, vaults, fee configuration and the fee recipient.
They retain captured authorities; the launcher does not possess those keys.

Use `--port` and `--studio-port` to select alternate ports, or `--surfpool` for an
explicit binary. Occupied ports fail before another server starts. Run
`python3 localnet/surfpool.py --check` to verify initialization and then stop.
Logs and readback reports are stored under ignored `work/surfpool/`.

## Execute signed transaction tests

```sh
work/localnet/venv/bin/python localnet/test_transactions.py
```

This validates the frozen fixture hashes, creates a disposable copy, and runs four
transaction sequences in fresh offline in-memory Surfpool instances. It then runs
all seven independent receipt-verification scripts on the new results:

- Authorized configuration updates and wrong-authority rollback.
- PumpSwap buy/sell, missing signer and slippage rejection.
- Fresh token/curve creation, curve trades, completion, migration and post-migration trades.
- Fees withdrawal, missing signer, wrong claimant and redirected recipient rejection.

Test signers, user balances and certain authority fields are synthetic. Each
receipt records signed payloads, errors, before/after state, balances and log output.
The resulting `transaction-summary.json` counts unique signed payloads across the
receipts. Output directories are new for each invocation; `--output` can specify a
new path. Imported evidence is never overwritten. Tests use ports 19831/19832,
19851/19852, 19871/19872 and 19891/19892 and reject port collisions.

## Scope

The network is offline, with auto-deployment disabled and no mainnet broadcasts.
Programs are the **original captures**, not rebuilt candidates. Local execution uses
the legacy BPF loader and strips only verified zero allocation padding after the
ELF section table. Upgradeable-loader metadata/authority behavior is not reproduced.
The accounts are selected captures from different slots, not a complete historical
chain snapshot. The imported transaction suite does not exercise Mayhem trades.
Passing transactions or readback checks do not establish source reconstruction or
complete byte identity. See the [reconstruction status](../repro/status.json).

[Surfpool documentation](https://www.surfpool.run/llms.txt) describes the local network
model; `surfpool start --help` lists the installed CLI's supported flags.

## Mayhem admin candidate parity

```sh
work/localnet/venv/bin/python localnet/mayhem_transactions.py \
  --candidate repro/mayhem/mayhem_recovered.so \
  --output work/localnet/mayhem-new-run
```

This freezes the candidate, runs 60 synthetic cases against both original and
candidate with valid transaction signatures, and compares committed errors, account
bytes/owners/lamports and payer/admin balance deltas. The recorded run passed all
60 comparisons (120 transactions). It covers ten admin handlers, including signer,
owner, writability and PDA checks. Timestamp-sensitive event logs are retained but
not compared. It does not exercise Mayhem trading or privileged PDA signing.
See [summary](evidence/mayhem-summary.json) and [full receipts](evidence/mayhem-transactions.json.gz).

The [lifecycle summary](evidence/transaction-summary.json) records 30 unique signed
transactions, 15 successful and 15 expected rejections. Compressed fresh receipts
and fixture readback hashes are also retained in `evidence/`.

### Donation forwarding reconstruction checks

[Donation draft and receipts](recovery/fees-donation/README.md) contain a partial two-handler Fees reconstruction, 713 signed LiteSVM differential cases and 10 original/candidate Surfpool comparisons (20 signed transactions). The draft remains byte-unequal to the captured full Fees program.

### Social fee reconstruction checks

[Social draft and receipts](recovery/fees-social/README.md) contain three recovered Fees handlers, 1,562 deterministic signed differential cases and 29 Surfpool comparisons (58 signed transactions). The draft remains byte-unequal to the complete captured Fees program.

### Referral withdrawal reconstruction checks

[Withdrawal draft and receipts](recovery/fees-withdraw/README.md) cover 113 signed differential cases and 16 Surfpool comparisons (32 signed transactions), including native SOL and SPL Token/Token2022 withdrawals. This single-handler draft remains byte-unequal to the complete Fees program.

### Fee-sharing creation reconstruction checks

[Sharing creation draft and receipts](recovery/fees-sharing/README.md) cover 116 signed differential cases and eight Surfpool comparisons (16 signed transactions), including genuine Pump and PumpSwap CPI migrations and account resizing. The single-handler draft remains byte-unequal to the full Fees program.

### Buyback reconstruction checks

[Buyback draft and receipts](recovery/fees-buyback/README.md) recover four handlers with 1,249 signed differential cases and 18 Surfpool comparisons (36 signed transactions), including initialization, authority update, signed funding and a sweep. The draft remains byte-unequal to the full Fees program.

### Administrative sharing reset reconstruction checks

[Administrative CTO draft and receipts](recovery/fees-admin-cto/README.md) cover 63 differential cases and 12 Surfpool comparisons (24 signed transactions) through the captured Pump caller. Pump performs its genuine PDA-signed CPI; transaction signers are test-owned keys. The Fees draft remains byte-unequal to the complete program.

### Fee-share update reconstruction checks

[Sharing-update draft and receipts](recovery/fees-sharing-update/README.md) recover both update handlers with 417 differential cases and 19 Surfpool comparisons (38 signed transactions), including old-shareholder payouts, Token2022 ATA creation and atomic rollback on invalid updates. The draft remains byte-unequal to the complete Fees program.
