# Boost buy-and-burn recovery

The AMM36 checkpoint implements `boost_buy_and_burn`, bringing the candidate to 36 of 38 published IDL handlers. All 24 AMM suites pass 16,727 comparisons against its exact executable, including 506 new boost cases. `create_config` and `multi_hop_swap` remain absent. This is bounded source reconstruction; whole original and ELF-extent byte equality remain false.

The original wrapper is at 0xe4738..0xe4c68, account context at 0x8d7d0..0x90068, body at 0x1fed8..0x22c80, and exit at 0x90068..0x90660. The package preserves annotated read-only excerpts, the original hash, and the disassembly hash. No executable bytes were edited.

## Recovered behavior

The handler requires the nonzero configured boost authority, enabled boost flag, enabled buys, and nonzero effective virtual reserves. It caps requested quote input at the boost vault balance, subtracts Token-2022 quote transfer fees, checks real quote reserves against accrued fees, and computes constant-product base output using net quote input minus one. Positive output, minimum output, and the output-reserve bound are checked before CPIs.

It transfers quote from the boost PDA vault, burns base from the pool vault with pool PDA seeds, reloads supply and balances, and emits both BuyEvent and BoostBuyAndBurnEvent as log and event-CPI pairs. The trade event identifies the boost PDA as user and uses post-burn base supply except for Mayhem's fixed 1e15 supply. Pool bytes, virtual reserves and creator fees stay unchanged. The boost event identifies the configured authority and records gross input used and the resulting balances.

When the vault becomes empty, Token-2022 transfer-fee mints require writable quote-mint access, harvest withheld fees to that mint, then close the boost vault to the authority. Original error 6088 `QuoteMintNotWritable` is absent from the supplied IDL and is recovered from disassembly and ordinary signed observations. The writable requirement applies even when the calculated fee is zero.

## Validation and provenance

The new corpus covers amounts and exact slippage boundaries, payload truncation, signatures, account keys/ownership/layouts, pool arithmetic and flags, token mint/owner/frozen state, transfer-fee combinations, final draining, harvest/close authority, and validation precedence. Fixtures use test-owned authority signatures, synthetic local configuration/balances, and captured unmodified token programs. Every constructed transaction verifies its signatures. There is no live broadcast, fixed-admin substitution, or manufactured privileged PDA signature.

All prior 23 suites were rerun against the scratch executable. A clean main-path build produced the same whole-file SHA256, so prior receipts are reused by that identity. The maintained new harness was also run from `/tmp` against the main executable and its 506 cases are exactly equal to scratch; this replay adds no unique cases. The package binds source/lock/compiler, runtime dependencies, test helper closure, actual executed commands and receipts. The failed first draft retains source and borrow-check diagnostics. Exploratory original-only probes are separate from counted differential evidence.

Candidate: 1,071,304 bytes; SHA256 `3018ca38e87cc9c984b4cfbd42aae1671fe82354da1bcb4211e085fba6869384`. The v1.44 compatibility dependency graph is unchanged from the preceding checkpoint and remains unproven as the historical graph. See [the immutable package](../../repro/pump_amm/boost-burn-thirty-six/README.md) and [compiler provenance](../../repro/pump_amm/compiler-v144/README.md).
