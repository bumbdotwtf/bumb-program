# Partial Fees sharing-config creation recovery

This package recovers only `create_fee_sharing_config`. It is **not** a complete Fees program, exact byte reconstruction, or deployment replacement.

Candidate: **288120bytes**, SHA-256 `8551d3530b0c957b0fa927994ceffc799683d5e3c119f4f02b465426249f68af`. Original: **948944bytes**, SHA-256 `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e`. **Full byte equality is false.**

## Source and observed behavior

The frozen `crate/` contents match the build3 source hashes in `build-comparison.json`; the original build ran from `work/fees-sharing-recovery/crate`, then was copied here. Anchor0.31.1 and exact lockfile are retained. Build toolchain/compiler/SDK hashes and comparison are recorded alongside `build.log`.

Creation uses captured Pump/PumpAMM program CPI to migrate curve and pool creator ownership to the sharing-config PDA. The recovered source initializes a temporary SharingConfig using the curve creator for the Pump CPI, then updates its admin/shareholder using the pool creator for the AMM CPI when applicable; final version is2. The program signs only its own seeds during CPI. Tests use ordinary test-owned payer signatures with signature verification enabled; no privileged signer injection or live writes occur.

Observed ordinary creation allocates1024bytes for sharing state; graduated migration expands the pool261→301bytes; the short-curve case expands the bonding curve82→166bytes. Existing nonzero-version state is retained. Invalid creator, missing required pool, and malformed contexts reject with the captured program's behavior.

## Verification

- `differential.json.gz`: **116/116** signed synthetic LiteSVM cases matching original/candidate errors, sharing/curve/pool state and balance fields, payer balances, events, and inner instructions. Captured Pump/PumpAMM programs perform genuine CPI.
- `surfpool-transactions.json.gz`: **8/8** matching cases and **16** actual normally signed transactions on pinned offline Surfpool1.6.1. Includes ordinary creation, graduated migration, missing pool, existing nonzero state, version0 initialization, short-curve reallocation, wrong creator, and wrong event PDA. No unexpected original errors.
- Surfpool compares all fixture and message-account data/owners/lamports/flags, errors, event payloads and return values. Only event timestamps and intentionally different Fees executable byte hashes/lengths are excluded. Program owner/funding/flags still compare. Raw snapshots, signed transactions, logs, timestamps and returns are preserved.
- Pump/PumpAMM share the ExtendAccountEvent discriminator but place the timestamp at different offsets. The runner attributes the emitting program through invocation-stack logs and normalizes Pump offset88 versus PumpAMM offset8. Other observed migration/creation events use offset8.
- `surfpool-fixtures.json.gz` contains exact synthetic fixtures and seed transactions. `manifest.json` hashes package files and maintained fixture/runner scripts. Dependency hashes are in the transaction receipt.

Re-run from repository root using fresh output paths:

```sh
work/localnet/venv/bin/python scripts/fees_sharing_create_differential.py --candidate localnet/recovery/fees-sharing/pump_fees_candidate.so --output work/fees-sharing-recovery/recheck.json
work/localnet/venv/bin/python localnet/sharing_transactions.py --candidate localnet/recovery/fees-sharing/pump_fees_candidate.so --output work/localnet/sharing-recheck
```

The Surfpool runner uses loopback RPC19991/WS19992, starts offline and shuts down after each run. Passing these cases does not establish exhaustive input equivalence or whole-program source/compiler identity.
