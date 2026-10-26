# PumpSwap v2 trading recovery

The independently implemented candidate includes `buy_v2`, `sell_v2`, and
`buy_exact_quote_in_v2`. Acceptance is bounded by the versioned differential
receipts below; this is not the original source, byte identity, or an exhaustive
security audit. The v1 trade, multi-hop, pool creation and fee-sweep paths remain
separate recovery work.

## Pricing and fees

The v2 paths deserialize the external Fees-owned configuration directly rather
than invoking Fees. Canonical Pump pool creators select market-cap tiers; other
creators use flat fees. SOL and the second normal quote use the normal table,
USDC uses stable tiers, and exotic quotes use exotic flat fees with zero-table
fallback. Market cap uses quote reserves plus signed virtual reserves and the
base supply. Mayhem pools use the fixed 10^15 supply. The captured original
accepts mayhem v2 trades and disables buyback; the published unused error name
`MayhemPoolNotSupported` is not evidence that the branch rejects them.

The account wrapper requires a complete Borsh fee configuration body with normal
Anchor discriminator/deserialization errors. Fee selection separately gates
stable tiers at 4,073 allocation bytes and exotic flat fees at 4,097. Below 2,512
bytes the handler returns 6083; empty selected tiers return 6082. A valid short
Borsh body in a larger account and an allocation cut through the body are distinct
cases. The suite tests both, plus unsorted/duplicate tier thresholds.

Buy computes the constant-product quote with upward rounding; sell rounds down.
Individual fees round up. Exact-quote buy estimates the quote before fees,
computes rounded fees, limits that estimate by the available remainder, and
subtracts one quote unit when computing base output. The event's quote fields
retain the original meanings even when they differ from the final transferred
amount. Synthetic extreme fee parameters exercise truncation, overflow and
insufficient-fee errors rather than assuming ordinary fee ranges.

Protocol fees after buyback and creator fees accumulate in Pool. Virtual quote
reserves decrease by the same accumulated sum, preserving their offset. The
unclaimed creator fee event field reports the updated stored counter. Holder
reward fields mirror creator fee values when that pool flag is set. A zero coin
creator suppresses the creator fee amount but does not erase the selected fee
basis points in events.

## Accounts and token calls

The user volume PDA is initialized to 137 bytes when absent. Existing user and
counter fields are preserved; events report applicable existing counters. Legacy
Pool allocations grow to 287 bytes, with a real System rent transfer when needed.
Disable checks precede the handler's resize. The buyback account is checked in
the handler for token-program ownership, quote mint, authorized token owner and
its associated-token address. It is not created by these paths. Self-event program
identity is checked as a typed Program account.

The suite runs the exact captured SPL Token and Token2022 binaries. Transfers use
TransferChecked and the expected user or pool PDA signer. Base transfer fees are
not grossed up. Quote transfer fees are accounted for in user slippage. Buyback
transfers retain their gross amount, while the event reports the received amount;
the event's final u64 reports the user/pool quote transfer fee. Exact-quote trades
can leave a remainder when splitting transfer-fee-bearing quote payments.

The captured program panics when synthetic corrupted buyback configuration makes
the buyback fee exceed protocol fees. The reconstruction preserves that observed
failure, including sell transfers before the failing calculation. This does not
establish a reachable production exploit: the recovered configuration setter
rejects buyback basis points above 10,000. All failure cases compare rollback and
inner instruction order.

## Verification boundary

Tests compare complete involved account bytes, owner and lamport state, errors,
log events and exact inner CPI instructions. Compute use and source-location text
are excluded. Accounts, signers and balances are disposable local fixtures; no
network transaction is submitted. Canonical and noncanonical pools and quote
mints are reconstructed as valid synthetic PDAs around captured state. These are
additional behavioral checks, not archived production pre-state.

Transfer hooks, confidential transfers, every extension combination, v1 trading,
ATA creation, migration and multi-hop routes are not claimed covered by this suite.

## Versioned checkpoint

`repro/pump_amm/trade-seventeen/` preserves the clean build, source/lock/toolchain
hashes, source/test snapshot and all eight full differential reports. The same
544,656-byte candidate passes **10,937 cases** with zero observed mismatches:
870 v2 trades and 10,067 earlier-handler cases. Its SHA-256 is
`4e509520c9f6cda114578f246e01fafc88bb2579ef0b913b1212543194153dfb`.
The unmodified whole-file original comparison fails, first at byte 24. Twenty-one
published instructions remain unimplemented. Passing these bounded tests does not
change that incomplete scope or establish a production-ready replacement.
