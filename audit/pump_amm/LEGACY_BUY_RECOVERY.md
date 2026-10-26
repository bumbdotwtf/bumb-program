# PumpSwap legacy buy and exact-quote recovery

AMM35 adds `buy` and `buy_exact_quote_in` and corrects zero-fee cashback sell event
classification. All 23 offline suites pass 16,221 comparisons on one clean v1.44
executable: all 15,194 previous cases, 16 new sell regressions and 1,011 buy-family cases.
The main executable is 1,034,280 bytes, SHA-256
`657ee4e28efa4d65e44347cd92c2a98c143c9e04055ab31f06002ea19f2caccd`.
The immutable package is `repro/pump_amm/legacy-buy-thirty-five`.

The two buy bodies use the actual captured Fees CPI, original legacy account ordering
and direct payouts. The missing optional bool payload defaults false; malformed values
reject. The accumulator is initialized during account validation and its user field is
updated. Existing volume fields remain unchanged in observed paths, even when the track
flag is true; the flag is preserved in the event. Global volume account type/seeds are
validated. The exact-quote event's field meanings are recovered separately from v2.

Only the pool deposit is grossed up to cover its quote transfer fee. Protocol, creator,
cashback and buyback transfers use their stated gross amounts; the buyback event field
reports net received tokens. Cashback creates its remaining ATA through actual CPI,
pays it and adds earned cashback before checking pool-v2. Slippage, overflow, zero-fee
skips and remaining-account errors preserve observed ordering and rollback.

Coverage includes amount/payload/slippage boundaries, typed account identity, ownership,
writability and layout, quote families, Token-2022 transfer fees, creator overrides,
Mayhem/holder flags, fee tables, accumulator fields, pre-funded account creation,
self transfers and conditional remaining accounts. Tests use normal verified test-owned
signatures and explicitly synthetic state with unmodified captured dependencies. Existing
migration suites use real original-program PDA CPI signing. No live calls or executable
modifications are performed. This does not establish exhaustive or historical equivalence.

Two unsuccessful source drafts are preserved with verified source snapshots, build logs,
harnesses and signed differential receipts. The earlier AMM33 event mismatch and its
negative receipt are retained; the new correction record links its exact original
transaction/results to a passing regression. Main/scratch whole-file identity binds the
existing suite receipts. Both maintained legacy harnesses are also replayed from `/tmp`
against the main executable, with identical case results and no additional unique count.

Whole-file and parsed ELF-extent equality against the captured original remain false.
The first differing byte is 24; 573,585 shared positions differ. Three IDL bodies remain
absent: `boost_buy_and_burn`, `create_config` and `multi_hop_swap`. Compiler/graph pins are
compatibility evidence, not proof of historical dependencies. The frozen security scan
and prior recovery packages remain unchanged.
