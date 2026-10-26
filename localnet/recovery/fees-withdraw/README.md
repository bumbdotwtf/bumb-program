# Partial Fees referral withdrawal recovery

This package recovers **only the `withdraw` handler**. It is not a complete Fees program, an exact byte reconstruction, or a deployment replacement.

The candidate is 239,752 bytes, SHA-256 `2548d08a38d3cbc3792fca666a6d9c299ea35227651bc6c2c8d1f598afaabe91`. The captured original is 948,944 bytes, SHA-256 `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e`. **Full byte equality is false.**

## Source and build

`crate/` contains the frozen Anchor0.31.1 source and lockfile used for the independent clean build at `work/fees-withdraw-recovery/crate`. `build-comparison.json` records original source paths/hashes, exact build command, selected platform-tools v1.52, compiler and SDK hashes, and byte comparison. `build.log` retains compiler output. The source was copied here after verification; this package directory was not the original build path.

The caller signs normally with its own user key. The referral vault is a system-owned PDA at `[b"referral-vault", user]` under Fees. Native withdrawals retain the zero-data rent floor; token withdrawals move the entire source balance using TransferChecked. Token source/destination must have the expected mint, authority and token program, but need not use ATA addresses. Optional account validation and errors follow the captured binary. No live writes or privileged signer injection were used.

## Verification evidence

- `differential.json.gz`: **113/113** matching normally signed LiteSVM cases. Compares errors, fixture account states/balances before and after, event bytes, inner instructions, and return data. Includes all16 optional-account combinations, native rent boundaries, Token/Token2022 paths, arbitrary valid token accounts, type/owner/mint/authority/readonly failures, missing accounts, and selected error-precedence cases.
- `surfpool-transactions.json.gz`: **16/16** matching cases, **32** actual signed transactions submitted to pinned offline Surfpool1.6.1. No unexpected original errors. Compares account states/balances, errors, events and return data. Only the decoded event timestamp is normalized across independent processes; raw timestamps, logs, returns and transaction bytes are retained.
- `surfpool-fixtures.json.gz`: exact synthetic account inputs and original fixture transactions used for Surfpool replay. Captured SPL Token, Token2022 and ATA dependency hashes are recorded in the transaction receipt.
- `manifest.json`: hashes every packaged file plus the maintained harness and runner used for verification.

Re-run from repository root, choosing a new output directory:

```sh
work/localnet/venv/bin/python scripts/fees_withdraw_differential.py --candidate localnet/recovery/fees-withdraw/pump_fees_candidate.so --output work/fees-withdraw-recovery/recheck.json
work/localnet/venv/bin/python localnet/withdraw_transactions.py --candidate localnet/recovery/fees-withdraw/pump_fees_candidate.so --output work/localnet/withdraw-recheck
```

Surfpool uses loopback RPC19981 and WS19982 and shuts down after each original/candidate run. The runner filters out the fixture's existing compute-budget instruction before adding a unique limit, signs using test-owned keys and verifies signatures before simulation/submission. Both processes operate offline. These tested behaviors do not establish exhaustive equivalence of all inputs or source/compiler identity.
