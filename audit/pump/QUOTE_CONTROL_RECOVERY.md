# Pump quote-control recovery

Six independent quote-control handlers are integrated into the prior frozen Pump42 source: `initialize_quote_control`, `set_quote_control_admin`, `set_quote_control_reserves_admin`, `add_quote_control_mint`, `remove_quote_control_mint`, and `set_quote_control_mint_reserves`. The resulting checkpoint contains 48 recovered handlers plus the existing partial v3 and create_v2 paths. Only `src/lib.rs` and four new files under `src/quote_control/` changed; the existing consumer in create_v2 and all trade source remain unchanged.

The original workspace draft was found outside main. Its account layouts, argument order, PDA seeds, authority constraints and events were reconciled with the captured IDL and current `Global`/`PumpError` definitions before a fresh build. The full old crate was not imported. Old scripts and saved successes/failures are retained under `historical-unaccepted/` in the new package. Their incomplete source/binary bindings are not acceptance evidence. The old static report also records a candidate hash different from the binary currently at its path.

The pinned v1.44 clean main and scratch builds are identical across the entire unmodified ELF: 1,478,960 bytes, SHA-256 `c9c364b59fca69ecc395c1e7911d55fc7997631daa0dd0b0bcf37d7f0dfa4804`. The package binds 35 local compiler inputs, 87 maintained helper files and 27 runtime fixture files. Cargo lockfiles, build attempts, logs, SDK/toolchain metadata, source archives and both stripped/unstripped outputs are retained. This records local build provenance without claiming a hermetic historical compiler/dependency reconstruction.

All fresh tests pass:

| Evidence | Scope | Result |
| --- | --- | --- |
| Prior main42 differential suites | 35 unchanged suites | 8,654 comparisons, zero mismatches |
| New quote-control suite | Six handlers, 507 cases | 507 comparisons, zero mismatches |
| Prior Surfpool runners | 28 unchanged runners | 1,024 comparisons, zero mismatches |

The quote-control suite executed 1,014 ordinary signed transactions containing 2,008 verified individual signatures. It uses synthetic QuoteControl accounts and normal test-owned authority keys, with explicit signature verification and recent-blockhash checking. Complete transaction bytes, before/after tracked accounts, CPI records, events, return data and logs are saved. All 800 failed original/candidate executions preserve nonpayer state and change the payer only by the expected signature fee. The original and candidate receive identical signed transaction bytes. No transaction is broadcast and no privileged/PDA signer is bypassed.

The six-handler counts are initialization 11, admin rotation 21, reserves-admin rotation 21, add mint 209, set mint reserves 180, and remove mint 65. Cases include role authorization, malformed and readonly accounts, missing state, event constraints, default/native/duplicate/missing mints, reserve boundaries, account padding, rent top-ups and list capacities around 50 and 256. The two fresh initialization privilege cases use a distinct fee payer so transaction privilege union cannot accidentally restore the signer/writable property being tested. The old 491 case definitions were draft leads; all outcomes were produced afresh. Repeated portability runs are preserved but counted only once.

The maintained runner is `scripts/pump_quote_control_fresh_differential.py`. It discovers the repository independently of the working directory, always binds the candidate/original/harness/IDL/config inputs, and binds the adjacent build report and its explicit source bytes when available. The final portability rerun produced the same complete transaction/outcome list as the initial fresh focused run. The old two quote-control scripts remain unchanged and are not the current CI entry point.

The 28 prior Surfpool runners executed 2,048 signed transactions containing 2,980 verified individual signatures. These are separate transaction/signature counts. They establish fresh regressions for prior handlers against the new executable; new quote-control coverage is the focused LiteSVM suite. No receipts from the prior candidate are reused. Fresh scratch receipts apply to main because the complete clean-built executables are identical.

Read-only static analysis finds bounded full-body matches for 13 of 23 selected quote-control functions after normalizing only actual ELF relocations and relative internal call offsets. Direct target checks are retained and do not all match. This does not prove transitive data equality, exact historical source, or full original-program byte identity. Full original-byte equality remains false.

The existing `sell_v2` quote transfer-fee minimum/output and fee-event gap remains explicit and unchanged; the old passing suite does not cover that boundary. Partial v3 trade, token-extension and depth-one nested-creation limits remain unchanged. No work was performed on the stopped fee correction, Pump incentives, v3 token extensions/fees or the stopped Mayhem initializer. There were no binary patches, padding changes, optimizer variants or source-layout searches.

The immutable package is [`repro/pump/quote-control-fortyeight`](../../repro/pump/quote-control-fortyeight/README.md). Its `manifest-sha256.json`, `main-scratch-identity.json`, `source-harness-sha256.json`, `independent-verification.json` and receipt-copy map bind current evidence. `verify-package.py` verifies saved files, current source and signed transaction bytes without executing program instructions. `replay-commands.json` lists the 36 differential and 28 Surfpool runners.
