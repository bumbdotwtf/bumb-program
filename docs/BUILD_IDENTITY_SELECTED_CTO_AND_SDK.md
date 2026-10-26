# Selected CTO code, SDK resolver gaps and dependency versions

Whole-file acceptance remains **0/4 core programs, 2/5 dependency capture images and 1/5 raw dependency compiler outputs**. This follow-up records immutable PR12head67608d457c096cebf73f1685f78f2f0ab9f9bdb0. Integration update: PR11headf914d0f0e70534212431b761d174a96e0fb7ba99 passed24/24 hosted jobs and merged as594bc7913943ea186087c9f5a7e39aefe3d3ab98. PRs10/12 were marked merged by ancestry. Active source/workflows match the independently checked PR12 head. The post-merge main run is separate. The complete [pass27 inventory](https://github.com/lalalune/pumpfun-source/blob/67608d457c096cebf73f1685f78f2f0ab9f9bdb0/repro/layered-passes/pass-27/README.md) and [pass26 remaining-byte report](https://github.com/lalalune/pumpfun-source/blob/67608d457c096cebf73f1685f78f2f0ab9f9bdb0/repro/layered-passes/pass-27/reconstruction-pass-26.md) retain all3,338 original queue records and every program/dependency gap. Nine reviewed CTO bodies are not a completion percentage.

## The selected constant correction already exists

The [Git-authenticated selected-artifact review](../repro/pump/pr12-selected-cto-review/README.md) binds Pump candidate71ec4d8a646eefc82ba177afbc3d08552deadd65cf2f80ec280862eb768d059c and symbols6edbf4dedf535dd0dec1199ab87a97d6d83b60fb2c1c3a5791feffc953a33cda to both the root37source inputs and compiled snapshot37 at that exact PR head. Sixteen authentic commit/tree objects and committed blob hashes are independently replayable without Git or a working source tree.

The selected6091 guard already uses SPL native_mint::ID and a direct32-byte WSOL literal. Its three actual calls are memcmp; the isolated f290 candidate's extra runtime conversion call is absent from this guard. Both6019 comparisons retain zero-target rejection before holder-PDA/sharing-key checks. The6019/6091 and early6092 constructors use named owned Anchor errors. A duplicate constant refinement build is unnecessary. The [earlier isolated build](../repro/pump/cto-6019-6091-controlled-build/README.md) remains preserved and UNSELECTED; its source-only constant proposal is historical, superseded by the implementation already selected in PR12.

| CTO part | Selected bounded evidence | Still missing |
|---|---|---|
|6019|Two ordered32-byte comparisons; named InvalidCreator; owned conversion/common return|Genuine holder-PDA changed-disjunct runtime coverage, exact origins, whole-caller/cleanup identity|
|6091|FeeSome/default/directWSOL/soleGlobalwhitelist; named error; no extra WSOL decoder in this guard|Genuine explicit-WSOL disjunct runtime coverage, exact origins, complete data/caller identity|
|Early6092|Named CtoCreatorAccountNotWritable, full28-byte name/75-byte message, owned160-byte conversion|Original eligibility and header evaluation order, account ownership/retention, genuine changed-branch acceptance|
|Late6092|Actual numeric ProgramError path remains visible|It is not a second recovered original constructor; immutable-flag domination and composition remain qualified|
|Ordinary wallet|Existing source is retained|Old-holder/shared eligibility propagation and shared operand order; ATA prelude once/before payouts; actual-quote WSOL selection; native recipient rent gate; native event quote bytes|
|Shared holder path|Existing source is retained|Positive frozen AMM/source vault6093 rejection and complete shared settlement/CPI/cleanup composition|

The fee-guard WSOL correction does not fix the separate wallet native selector, which still tests raw curve.quote_mint==default. [Complete wallet-effect evidence](../repro/pump/cto-wallet-effects-static-20261025/README.md) retains35 original bodies and independent checks. Its integrated patch describes an older baseline and is not automatically applicable to PR12's already named early6092. Its five remaining effect gaps remain real work; no full wallet implementation is claimed.

Selected natural origins are src/admin_cto.rs16bytes at107/108/115, versus original programs/pump/src/creator/admin_cto.rs38bytes at312/326/556. Owner-before-executable evaluation and late numeric6092 remain different. No hardcoded coordinates, line padding, path remapping or binary edits are used. Complete parser/callback, account ownership, allocator/OOM, transitive data/CPI/error/cleanup and ABI identity remain unproved.

## Four more SDK account objects, with resolver obligations retained

The [ordinary swap follow-up](../repro/sdk/ordinary-swap-followup-20261025/README.md) authenticates Pump SDK4.3.1 and PumpSwap2.2.0 archives and enumerates their identical21-field swapAccounts helpers. Ordinary AMM buy/sell in each package now have unique symbolic bindings. The original a208 matrix and earlier liquidity follow-up remain unchanged.

| Per SDK package | Explicit named fields | IDL resolver recipes outside the helper | Extra helper fields |
|---|---:|---|---|
|AMM buy|19/23|globalVolumeAccumulator, userVolumeAccumulator, feeConfig, feeProgram|buybackFeeRecipient, buybackFeeRecipientTokenAccount|
|AMM sell|19/21|feeConfig, feeProgram|The same two buyback fields|

The extra fields are appended through remainingAccounts, not silently inserted into named IDL slots. Conditional cashback/user-volume and pool-v2 accounts also remain. Complete ordinary methods, helper objects, every IDL row/address/seed, extra/default fields and historical Rust contexts are retained. Field order is reconstructed from IDL, not object insertion order.

Eight of the original25 nonliteral object sites have now been expanded symbolically: four liquidity and four ordinary swaps. Seventeen other sites remain unexpanded. **All four new swap routes remain open for complete runtime compatibility**: Anchor resolution, numeric PDA/ATA derivation, remaining-account ordering/flags/state, fee selection, withBuyAccounts/withSellAccounts wrappers, external constants and exact JavaScript dependency resolution are unexecuted/unclosed. IDL resolver metadata prevents treating an omitted explicit field alone as a client bug. No stopped instruction or new SDK/runtime probe was followed.

## Version labels conceal distinct dependency families

The [selected version witness](../repro/build-tooling/pr12-dependency-version-witness/README.md) authenticates18 committed manifest/lock/vendor/status/build-receipt inputs through25 Git commit/tree objects. It preserves all locked names, versions, checksums, origins, patches, direct declarations and effective profiles.

| Selected source | Locked dependency facts |
|---|---|
|Pump/AMM/Fees|anchor-lang and anchor-spl0.31.1; attribute/derive macros and anchor-syn0.31.2; Borsh0.10.4 and1.8.1; SPL Token7.0.0/Token2022 6.0.0|
|AMM|solana-pubkey2.4.0 is explicitly patched to a captured local vendor tree; the version label does not authenticate the registry implementation|
|Fees|Uses root workspace lock/profile, with solana-pubkey2.2.1; Pump/AMM lock2.4.0|
|Mayhem|Anchor1.0.0 and solana-pubkey3.0.0/4.4.0; a different family from Pump/AMM/Fees|
|Relay|No Anchor crate in the selected lock; this witness proves lock absence only. Earlier Relay15 source packets describe its reconstructed owned-error implementation; no fresh implementation closure is inferred here|

The253/255/253/216/233 locked-package totals include local roots and potentially unused/host-only entries. They are not actual compiled-unit or on-chain linkage counts. Four retained core receipts explicitly select v1.44 for Pump/AMM/Fees and v1.54 for Mayhem. Default driver banners, SDK strip versions, compiler/sysroot identity, host-library closure and original deployment versions are separate evidence. Missing receipt fields are not invented. npm Anchor^0.31.1 and SPL Token ranges do not establish the resolved JavaScript graph or the Rust macro versions. No version/flags/library sweep is justified by these labels alone.

## Independent review and integration gates

A fresh detached PR12checkout passed current107/Relay23 bindings, complete metadata preserving all3,338records and both raw matrices, and portable saved-signature checks with Python3.12/solders0.27.1. All numeric exits and raw streams are retained in [the independent acceptance record](../repro/ci/pr12-independent-review/README.md). The checkout remained clean. No new compiler/VM/target execution or original-body collection ran. These checks are not an assertion of originating runtime byte identity.

Three earlier hosted runs at PR12 head were cancelled, so none counts as a pass. Existing PR run40251488654 was restarted once as attempt2. During verification, PR11 advanced to f914d0f0e70534212431b761d174a96e0fb7ba99 and incorporated PR12 plus both CTO evidence commits by ancestry. Its active programs/scripts/workflows/attributes/root manifests and lock are identical to the independently checked head; added records remained passive. All24 hosted jobs at f914 completed SUCCESS.

PR11 was merged with an exact-head guard into main594bc7913943ea186087c9f5a7e39aefe3d3ab98 on2026-10-26 at01:12:14UTC. GitHub then marked PR10 and PR12 merged by ancestry. This does not erase the preceding cancelled runs or reinterpret them as passes. Main push run40253060759 was queued at this report checkpoint. The now-obsolete root-initiated PR12attempt2 was cancelled after the complete newer head passed; it is not a pass. Any newer main/data publication still needs its own observed state. Full identity remains0/4; the broader reconstruction goal is active.

Publication whitespace check retains three authenticated input findings: root Cargo.toml EOF in the version witness, and cashback trailing/create_v2 EOF in the selected compiled snapshot. Their source bytes, Git blob bindings and owning manifests are unchanged. The metadata-only whitespace check passes with those two whitespace classes disabled for the command; no .gitattributes or active guard asset is changed.
