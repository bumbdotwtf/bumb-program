# Reconstruction progress, pass17

Verified checkpoint branch: `codex/layered-reconstruction`. Remote main received overlapping changes; this report describes the independently verified pass17 artifacts.

Integrated AMM Claim self-transfer admission, Fees sharing missing-pool error ownership, and Relay IDL header-read error ownership. Both core main builds reproduce the tested executables and symbols. All53,787 existing core comparisons remain passing; Pump retains1,024 Surfpool comparisons and Relay retains12 ordinary cases. No overall reconstruction percentage is inferred from these finite checks.

# Complete remaining byte comparison

The exact acceptance result is **0/4 core programs** and **2/5 dependency capture comparisons**. Every original byte is included. Different-position counts include only the common file extent; excess bytes are reported separately. Layout changes make these counts unsuitable as a completion percentage.

| Program | Original bytes | Candidate bytes | Different common positions | Excess bytes | Exact |
| --- | ---: | ---: | ---: | ---: | --- |
| pump | 10,485,715 | 1,582,192 | 881,460 | 8,903,523 | No |
| pump_amm | 10,485,715 | 1,198,824 | 671,861 | 9,286,891 | No |
| pump_fees | 948,944 | 849,984 | 468,821 | 98,960 | No |
| mayhem | 777,408 | 668,640 | 362,490 | 108,768 | No |
| spl_token | 108,600 | 108,600 | 0 | 0 | Yes |
| spl_token_2022 | 1,382,016 | 1,382,016 | 0 | 0 | Yes |
| associated_token | 105,032 | 105,032 | 307 | 0 | No |
| token_metadata | 793,991 | 793,991 | 1,509 | 0 | No |
| donation_relay | 830,448 | 470,560 | 257,397 | 359,888 | No |

SPL Token is a raw compiler output. Token-2022, ATA and Metaplex rows use existing retained allocation images; [raw compiler supplements](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/layered-passes/pass-17/after-corrections/summary.json) remain separate. No image is padded or modified in this pass. The [complete compressed interval ledger](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/layered-passes/pass-17/after-corrections/all-byte-ranges.json.gz) contains every mismatch interval and excess range.

## Function, call and data inventories

The [machine-readable index](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/layered-passes/pass-17/current-analysis-index.json) binds the complete ledgers below to exact current original/candidate hashes. It preserves full rows rather than selecting only successful matches. These methods differ; their window and pair counts must not be combined into a percentage.

- [Pump: complete before/after inventory (use after)](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/pump/creator-full-curve-fortyeight/full-before-after-inventory.json.gz) — candidate `f8d6f75a4dd285257aa6e9af3bcad7bf857bd7cef65a3a859ccbdb844a91c0cd`.

- [AMM: complete residual ledger](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/pump_amm/claim-self-transfer-v144/inventory/after/residual-ledger.json.gz) — candidate `ad74b08447914cb219624f9e9cc81d4cfe751b332d67534c45aec63ef70aa166`.

- [Fees: current full function inventory](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/pump_fees/sharing-owned-error-v144/analysis/full-function-inventory.json) — candidate `70ddf61ad431b950aefd736ac50da156c9079257ea95f32cfcd9635266e40429`.

- [Mayhem: complete residual ledger](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/mayhem/sell-result-error-twentyfour/static/complete-inventory.json.gz) — candidate `7d416f848f03e46d9a514f4c505a8e903cdb908f52280bb961254eed90aebe1f`.

- [Relay: complete original/candidate match ledger](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/donation-relay/source-build-10-idl-deserialize/match-ledger.json) — candidate `5af54232ebb9e8fef524f6f6984d6dbd4567874bcf4a6e6927501c3bca66e549`.

The [prior dependency review](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/layered-passes/pass-09/dependency-review/REPORT.md) still applies to hash-identical ATA and Metaplex candidates. The [six-hypothesis Fees review](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/repro/layered-passes/pass-10/fees-residual-review/REPORT.md) identifies three already-correct orders and three unresolved ownership/function-boundary questions.

## Outstanding work by program

| Program | Remaining source and acceptance work |
| --- | --- |
| Pump | Five partial handlers and three unrecovered dispositions; V3 decoder/preparation full body equivalence and new short-layout runtime acceptance; mode0 divergent-supply runtime coverage after the buy fee-input correction; the buy complete-before-cashback order is corrected but exact-quote caller attribution remains limited; whitelist admission, residual/settlement/event composition; broader routes and creation; unmatched code, transitive calls/data, diagnostics and build provenance. Stopped scopes stay stopped. |
| AMM | 302 original windows without normalized matches; scalar specialization, diagnostic/data and recursive call gaps; authentic successful initializer replay; whole ELF identity. The supported accumulator Clock/store order, claim overflow-before-store order and explicit self-transfer predicate are corrected; unrelated snapshot-load movement remains an unproven source hypothesis. Existing scalar evidence does not justify forcing a code shape. The prior restored claim context closed four additional normalized original windows; this pass preserves that count; raw identity, remaining data and indirect-call closure stay open. |
| Fees | 130 unattributed and two conflicting original windows; 118 unmatched and two conflicting candidate windows; full withdrawal/sharing and legacy/V2 caller, payout helper and compared-value CFG identity; legacy handler/parser/wrapper and AMM CPI differences; cleanup, data, diagnostics and source/build identity. |
| Mayhem | The reviewed typed zero-divisor errors are corrected in both BuyPumpSwap and SellPumpSwap. Other non-initializer source/error/ownership gaps, five unresolved GlobalParams roles, 61 retained diagnostic rows, build provenance and full identity remain. Initializer remains excluded. |
| ATA | 304 text and three relocation bytes; original build/source ordering is not established. The differing code is not the custom panic body. |
| Metaplex | 1,477 text, 30 diagnostic and two relocation bytes. Local transformed CFG correspondence does not establish raw equality or historical source. No additional runtime probe. |
| Relay | 370 original windows without normalized matches; remaining serializer/owned-error body, conversion and logging differences after the header correction, full call/data/error ABI; retained source-origin rejection, fixed-authority success routes and original build provenance. |
| All | Unknown transitive data extents, indirect calls, precise historical source/compiler/dependencies and incomplete security assessment. Normalized matching alone closes none of these globally. |

The exact incomplete instruction names and stopped-scope dispositions remain in [COMPLETION.md](https://github.com/lalalune/pumpfun-source/blob/4a66c4a3a7acfc8e6a48375bbd526d6f72b006ba/docs/COMPLETION.md). Published source contracts and finite regressions do not establish exhaustive semantics. The before/after snapshot, current index, package seals, build identities and saved receipt verification make this pass reviewable without claiming completion.
