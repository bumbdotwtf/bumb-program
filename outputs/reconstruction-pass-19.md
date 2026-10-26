# Reconstruction progress, pass19

Verified checkpoint branch: `codex/layered-reconstruction`. Integrated Pump admin-CTO typed curve state, AMM initializer user ownership, and Fees late account/state-exit ordering. All three main builds reproduce tested executables and symbols. All53,787 existing core comparisons remain passing; Pump retains1,024 Surfpool comparisons. Whole original identity remains0/4 core and2/5 dependency captures. These finite counts are not an overall completion percentage.

# Complete remaining byte comparison

The exact acceptance result is **0/4 core programs** and **2/5 dependency capture comparisons**. Every original byte is included. Different-position counts include only the common file extent; excess bytes are reported separately. Layout changes make these counts unsuitable as a completion percentage.

| Program | Original bytes | Candidate bytes | Different common positions | Excess bytes | Exact |
| --- | ---: | ---: | ---: | ---: | --- |
| pump | 10,485,715 | 1,580,712 | 882,041 | 8,905,003 | No |
| pump_amm | 10,485,715 | 1,200,544 | 673,561 | 9,285,171 | No |
| pump_fees | 948,944 | 849,472 | 468,533 | 99,472 | No |
| mayhem | 777,408 | 668,640 | 362,490 | 108,768 | No |
| spl_token | 108,600 | 108,600 | 0 | 0 | Yes |
| spl_token_2022 | 1,382,016 | 1,382,016 | 0 | 0 | Yes |
| associated_token | 105,032 | 105,032 | 307 | 0 | No |
| token_metadata | 793,991 | 793,991 | 1,509 | 0 | No |
| donation_relay | 830,448 | 471,192 | 257,767 | 359,256 | No |

SPL Token is a raw compiler output. Token-2022, ATA and Metaplex rows use existing retained allocation images; [raw compiler supplements](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/layered-passes/pass-19/after-corrections/summary.json) remain separate. No image is padded or modified in this pass. The [complete compressed interval ledger](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/layered-passes/pass-19/after-corrections/all-byte-ranges.json.gz) contains every mismatch interval and excess range.

## Function, call and data inventories

The [machine-readable index](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/layered-passes/pass-19/current-analysis-index.json) binds the complete ledgers below to exact current original/candidate hashes. It preserves full rows rather than selecting only successful matches. These methods differ; their window and pair counts must not be combined into a percentage.

- [Pump: complete before/after inventory (use after)](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/pump/admin-cto-typed-fortyeight/full-before-after-inventory.json.gz) — candidate `5d35884bf79de90850e23ac5e6781b328430b8748f62e4c1381cb77b9f2e0a6c`.

- [AMM: complete residual ledger](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/pump_amm/init-user-ownership-v144/inventory/after/residual-ledger.json.gz) — candidate `3fe52eea99e26866795348aad93fb821f834bf04290b4176a67ae0b7add0fcb5`.

- [Fees: current full function inventory](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/pump_fees/sharing-option-order-v144/analysis/full-function-inventory.json) — candidate `4baf4866909828f5017a86e595a72dc7f47b443ad4623597b2d532f9ca57778e`.

- [Mayhem: complete residual ledger](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/mayhem/sell-result-error-twentyfour/static/complete-inventory.json.gz) — candidate `7d416f848f03e46d9a514f4c505a8e903cdb908f52280bb961254eed90aebe1f`.

- [Relay: complete original/candidate match ledger](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/donation-relay/source-build-11-idl-discriminator/match-ledger.json) — candidate `34c54b8e1e625a46fd446bb8e6fa7c7f17afcb1fd7d2ef3719a16f630c98ce91`.

The [prior dependency review](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/layered-passes/pass-09/dependency-review/REPORT.md) still applies to hash-identical ATA and Metaplex candidates. The [six-hypothesis Fees review](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/repro/layered-passes/pass-10/fees-residual-review/REPORT.md) identifies three already-correct orders and three unresolved ownership/function-boundary questions.

## Outstanding work by program

| Program | Remaining source and acceptance work |
| --- | --- |
| Pump | Five partial handlers and three unrecovered dispositions; V3 decoder/preparation full body equivalence and new short-layout runtime acceptance; mode0 divergent-supply runtime coverage after the buy fee-input correction; the buy complete-before-cashback order is corrected but exact-quote caller attribution remains limited; whitelist admission, residual/settlement/event composition; broader routes and creation; unmatched code, transitive calls/data, diagnostics and build provenance. Stopped scopes stay stopped. |
| AMM | 297 original windows without normalized matches; scalar specialization, diagnostic/data and recursive call gaps; authentic successful initializer replay; whole ELF identity. The supported accumulator Clock/store order, claim overflow-before-store order and explicit self-transfer predicate are corrected; unrelated snapshot-load movement remains an unproven source hypothesis. Existing scalar evidence does not justify forcing a code shape. The earlier Claim context and new Sync context close six normalized original windows across their checkpoints; raw identity, remaining data and indirect-call closure stay open. |
| Fees | 130 unattributed and two conflicting original windows; 118 unmatched and two conflicting candidate windows; full withdrawal/sharing and legacy/V2 caller, payout helper and compared-value CFG identity; legacy handler/parser/wrapper and AMM CPI differences; cleanup, data, diagnostics and source/build identity. |
| Mayhem | The reviewed typed zero-divisor errors are corrected in both BuyPumpSwap and SellPumpSwap. Other non-initializer source/error/ownership gaps, five unresolved GlobalParams roles, 61 retained diagnostic rows, build provenance and full identity remain. Initializer remains excluded. |
| ATA | 304 text and three relocation bytes; original build/source ordering is not established. The differing code is not the custom panic body. |
| Metaplex | 1,477 text, 30 diagnostic and two relocation bytes. Local transformed CFG correspondence does not establish raw equality or historical source. No additional runtime probe. |
| Relay | 370 original windows without normalized matches; remaining serializer/owned-error body, conversion and logging differences after the header correction, full call/data/error ABI; retained source-origin rejection, fixed-authority success routes and original build provenance. |
| All | Unknown transitive data extents, indirect calls, precise historical source/compiler/dependencies and incomplete security assessment. Normalized matching alone closes none of these globally. |

The exact incomplete instruction names and stopped-scope dispositions remain in [COMPLETION.md](https://github.com/lalalune/pumpfun-source/blob/codex/layered-reconstruction/docs/COMPLETION.md). Published source contracts and finite regressions do not establish exhaustive semantics. The before/after snapshot, current index, package seals, build identities and saved receipt verification make this pass reviewable without claiming completion.

## Hosted validation follow-up

Pass 18 finished with 11 of 12 jobs passing. The remaining job passed its 2,299 comparisons, then rejected an outdated source-manifest binding before the extra nested-route candidate replay. The CI binding is repaired with an extracted, unchanged harness and the current successful main-build source map. The same 16 nested cases passed locally with 64 verified signatures. Hosted acceptance for the follow-up is still pending. See [the retained follow-up](https://github.com/lalalune/pumpfun-source/tree/codex/layered-reconstruction/repro/layered-passes/pass-19/ci-followup).
