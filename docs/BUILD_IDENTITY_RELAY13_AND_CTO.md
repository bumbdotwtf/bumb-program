# Relay13 compiler comparison and remaining CTO source gaps

Full original-byte acceptance remains **0/4 core programs and 2/5 dependency captures**. This follow-up adds measured compiler/library evidence and concrete source recoveries; it does not select a new artifact or claim complete reconstruction. The [previous review](BUILD_IDENTITY_PASS24_REVIEW_AND_LINUX.md), [per-instruction dispositions](COMPLETION.md) and [complete remaining-work inventory](../repro/layered-passes/pass-24/REMAINING.md) retain the broader scope.

## Actual selected-source compiler measurement

[Run 40209794148](https://github.com/lalalune/pumpfun-source/actions/runs/40209794148), attempt 1, measured frozen Relay13 at main 2508c2be. One build completed; compiler and strip returned 0 and no anchored backend Error appeared. All 23 source inputs stayed unchanged, with only src/idl.rs different from the real Linux12 control. The candidate is 501,576 bytes, SHA256 `506b11353f8eb15d079794656eaf6c10d1a8da2c50d2e90cbdbe949a3ecdd0fb`. It remains unselected at recording, with no new VM or transaction execution.

The exact uploaded ZIP and 73 exported files are retained. Its digest matches the saved GitHub artifact metadata. Independent review regenerates both full Linux ledgers and every one of the 492 original-window status/raw/normalized rows. All 492 statuses are unchanged from Linux12, despite 432 additional file bytes and 94,846 differing common positions. That is not evidence of a semantic improvement or regression.

The [complete packet and verifier](../repro/donation-relay/source-build-13-linux-v148-measurement/README.md) retain source, tool/cache attestations, actual root flags, full outputs and limits. Selected compiler/sysroot/strip bytes and stock cfg/spec agree with Linux12. Full host system-library identity is not established. Unexported tool/cache/archive bytes cannot be freshly rehashed from the publication alone.

## A measurable compiler/library mismatch

The same fixed method was independently rerun against prior selected Relay13's v1.44 recipe and the Linux v1.48 recipe. Their 23 source inputs, lock and profile match.

| Original windows | Prior selected recipe | Linux v1.48 recipe |
|---|---:|---:|
| Normalized, including raw |122|225|
| Raw |33|58|
| Unmatched |370|267|

Every prior match is retained: 103 normalized gains and 25 raw gains, with zero losses. The raw gains include 20 formerly unmatched windows and 5 upgrades from normalized-only matches. This materially strengthens the measured compiler/library finding; it does not attribute every difference to compiler version alone, because OS/native, stripping and cache/build context also differ.

Full before/after ledgers retain all alternatives and negatives. Candidate names do not identify original functions by themselves: the 72-byte multiply-wrapper shape has three alternatives, and actual callees reject two. The raw 1128-byte fmt body still has five indirect calls without complete callback closure. Code-window equality does not prove a complete data graph or runtime ABI.

The direct Unicode follow-up closes all six actual original/Linux13 tables: **1,449 complete bytes**, with true consumer bounds, strides, encoded ends and zero gaps/overlaps. Complete 696/704-byte bodies, their real call and immediate diagnostic/callee evidence are retained. This supersedes 64-byte sampling for these arrays. Outward panic/indirect/external-consumer closure remains open.

## Concrete CTO omissions and unfinished composition

The [historical-source recovery](../repro/pump/cto-remaining-errors-static-20261025/README.md) preserves full bounded original bodies, account packing, owned constructors, exact source paths, proposals and independent review. All proposed patches are unapplied in this publication.

For 6019, the original nonholder Some route rejects zero first, then the actual holder-rewards PDA, then sharing_config.key. Current source omits the holder-PDA comparison and returns numeric ProgramError. Both original equality failures use owned InvalidCreator, Source 312, no compared values and the 38-byte creator/admin_cto.rs path. A minimal guard-and-constructor proposal has independent static support. Emitted code and normally signed callable coverage remain separate gates.

For 6091, the prior [owning-field proof](../repro/pump/cto-6091-static-review-20261025/README.md) supports adding the explicit wrapped-SOL comparison and named owned CreatorFeeNotConfigurableForQuote. Current source omits that comparison and uses a numeric return. A controlled combined 6019/6091 candidate is being prepared separately; no successful candidate build is claimed here.

For 6092, the original has one owned constructor before quote-account frozen decoding. Current source has two numeric returns; the later one is dominated under the ordinary immutable AccountInfo contract. The old holder flag is now grounded through all nine historical account-reader layouts. Original cached eligibility excludes shared and old-holder routes before old-creator/System/non-executable/writable checks; current wallet lacks those exclusions. Original shared evaluation is key→owner→nonempty, while current source evaluates owner→nonempty→key. Borrow/panic order therefore remains relevant.

The downstream wallet amount, destination-ATA preparation, native/token selection, rent condition, payout/CPI/event and cleanup composition still requires exact caller/data-flow review. Correcting only an early error must not be represented as correcting every later use of wallet. Constructor-only proposals remain qualified; no complete payout identity or 6092 runtime acceptance follows.

The captured CTO filename is exactly `programs/pump/src/creator/admin_cto.rs`; the current path omits creator/. Exact bytes do not prove original Rust logical namespace or source formatting. No file remap, hardcoded Source coordinate or line padding is used to manufacture equality.

## Remaining work retains the full objective

Pump's partial/unrecovered instructions and larger handler/caller/settlement/event gaps remain. AMM's unmatched application windows and data/call closure, Fees' conflicting/unattributed windows and payout/ownership paths, Mayhem's unresolved fields/diagnostics, ATA's historical unit ordering, Metaplex's exact source provenance and Relay's 267 unmatched windows remain tracked in the complete inventory. Indirect calls and transitive data/ABI/security closure are not solved by normalized matches.

The SDK follow-up closes four symbolic liquidity account expressions; the other 21 previously nonliteral sites, dynamic resolver/wrapper behavior and exact resolved JavaScript dependency closure remain open. Existing excluded research stays inactive. Full acceptance still requires all original bytes, complete build provenance and the stated program/source/runtime obligations, rather than a smaller passing subset.

Main2508c2be's full hosted [12-job run passed](https://github.com/lalalune/pumpfun-source/actions/runs/40209730931). These baseline checks do not transfer runtime acceptance to the new unselected compiler artifact or unapplied CTO proposals.
