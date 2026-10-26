# PumpSwap legacy sell recovery

The source adds `sell` as the 33rd instruction body of 38. A clean v1.44 build and
22 offline original/candidate suites pass 15,194 comparisons: 14,635 prior AMM cases
plus 559 legacy sell cases. The candidate is 963,600 bytes, SHA-256
`043bedfd0fbf56fe4d5e39b69b713a24f5bbbe34e350c8a45b96919abfd368ca`.
The package at `repro/pump_amm/legacy-sell-thirty-three` binds the exact main source,
lock, compiler, harness closure, captured runtime dependencies and all receipts.

The legacy path uses an actual Fees `get_fees_with_quote_mint` CPI and prices the
requested gross base amount. Unlike v2 accrual, it pays protocol and creator vaults
directly while preserving the pool's existing virtual reserves and accrued counters.
Its real-reserve guard precedes token transfers. Quotes, transfer fees, configurable
creator fees, canonical authority, Mayhem and holder flags are covered by bounded
synthetic-state comparisons; these do not prove exhaustive extension equivalence.

A positive creator payout consumes a `pool-v2` remaining account. Cashback consumes
its ATA and accumulator first, creates/funds absent accounts through real System and
ATA CPIs, pays the ATA, overwrites the accumulator user and increases earned cashback,
then validates `pool-v2`. Errors after earlier CPIs retain the original instruction
order and transaction rollback. Buyback identity checks run even for zero fees and
Mayhem; a positive payout creates an absent ATA idempotently and the event reports its
net received amount. A zero fee does not create the ATA.

The new suite compares watched account bytes, owners and lamports, event payloads,
inner instructions, return data, errors and signed transaction bytes. It uses ordinary
verified test-owned signatures and unmodified captured dependency executables. Invalid
injected states are explicitly synthetic. No transaction is broadcast, no privileged
signer is supplied or bypassed, and no executable bytes or headers are modified.
Diagnostic log wording and compute consumption are excluded from equality.

Four unsuccessful drafts, their hash-verified source snapshots, compile logs and
runtime receipts are preserved. Earlier variants misplaced validation, used net base
pricing, omitted cashback, or created a zero-fee ATA; none is promoted. The final
main-path identity report states exactly which scratch receipts are reused.
The maintained harness is also replayed from an unrelated working directory against
the identical executable to verify portable path resolution and unchanged cases.

Whole-file and parsed ELF-extent identity remain false. The first different byte is
24. Five bodies remain absent: `boost_buy_and_burn`, `buy`, `buy_exact_quote_in`,
`create_config`, and `multi_hop_swap`. The v1.44 lock and compiler are compatibility
controls, not proof of the original graph. The prior AMM32 checkpoints and separate
frozen security scan remain unchanged.


## AMM35 event correction

A subsequent signed cross-case showed that AMM33's zero-fee cashback sell succeeds
with matching account state/payouts but mislabels creator/cashback basis points in the
event and event CPI. The immutable negative receipt is retained at
`repro/pump_amm/legacy-sell-zero-fee-gap`; AMM33 remains a historical affected artifact.
AMM35 changes classification only when `creator_fee > 0`. Sixteen added regressions
pass, and `repro/pump_amm/legacy-buy-thirty-five/sell-event-correction.json` binds the
original negative case to an exact original result and signed transaction in the new
passing sell suite. The current sell suite has 575 cases. See `LEGACY_BUY_RECOVERY.md`
for the AMM35 build, full 23-suite validation and executable identity.
