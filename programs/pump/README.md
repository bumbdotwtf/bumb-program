# Pump: CTO remaining guard and owned-error restoration

Tested scratch candidate `71ec4d8a646eefc82ba177afbc3d08552deadd65cf2f80ec280862eb768d059c` restores the non-holder target rejection for the holder-rewards PDA, explicit WSOL fee exclusion, and plain named owned errors6019/6091/early6092. The WSOL comparison uses the existing same-type SDK native-mint constant; emitted bytes compare the original32-byte value directly without runtime base58 on this guard. The late numeric6092 guard, account types, wallet evaluation order and prior6030/2006 compared-key fixes remain unchanged.

The unchanged9269 differential +1024 Surfpool corpus,68 receipt bindings and saved signature/effect assertions pass. Exact original/current application coverage is6019 one differential,6091 eleven differential,early6092 five differential plusone Surfpool. Application2006 coverage remainszero; parser failures do not close it. These counts do not establish that the new holder-PDA or explicitWSOL disjunct was exercised. All raw diagnostic differences and natural current source coordinates are retained; no whole original executable/log identity or exhaustive equivalence is claimed.

The original copied owned AccountInfo versus current borrowed UncheckedAccount, original executable-before-owner versus current owner-before-executable, late6092 reload and remaining parser/CPI/header ownership gaps remain explicit. The plain early6092 return has a direct original predicate/constructor counterpart under the admitted immutable-header domain; the source patch does not restore all parser/layout/drop behavior.

Evidence: [`repro/pump/remaining-guards-fortyeight`](../../repro/pump/remaining-guards-fortyeight/README.md). It retains exact37 source, full original/current function/call/data ledgers and bounded windows, actual v1.44 compiler/v1.52 strip/tool/SDK/dependency gates, isolated unchanged corpus, raw signed receipts and failures. The first successful f290 build emitted runtime base58 for the inline macro; that discrepancy and its complete evidence remain historical. The separately prepared const-only95b6 plan was not executed. One reviewed corrective build used the existing SDK constant and early-only owned6092; no flags, layout, coordinate tuning, new fixtures or stopped execution were introduced. Scratch acceptance alone is not a main build or current-selection claim.

<details>
<summary>Historical e949 compared-key checkpoint and inherited recovery history</summary>

# Pump: CTO compared-key owned-error restoration

Tested scratch candidate `e9494060904aad25f465efd93af9dd0bb09a5ded9f321747c789cbf0310bc6c5` restores original owned error construction for6030 `CreatorShouldNotBeZero` with `(target, Pubkey::default())` and application2006 `ConstraintSeeds` with `(actual holder_creator_vault, derived creator-vault PDA)`. Exact two-site source patch on accepted3ae/d9d source37 changes no guard predicate/order, account requirement, state mutation, borrow, rent or CPI behavior. The original full parser-to-account role and comparedLeft/Right proof is retained. Other numeric6019/6091/6092 occurrences remain unresolved.

The unchanged finite9269 differential +1024 Surfpool corpus and saved signatures/effects are retained in the scratch evidence, subject to its terminal acceptance records. Changed application coverage is one differential6030 case (`new-zero`) and zero application2006 cases; Surfpool reaches neither changed application branch. Parser2006 failures are separate and do not close that gap. Current source107/118 naturally differs from original307/648; no source-coordinate constants/remapping or whole executable/log identity is claimed.

Evidence: [`repro/pump/admin-cto-compared-errors-fortyeight`](../../repro/pump/admin-cto-compared-errors-fortyeight/README.md). It preserves exact37source, bcb source proof, full original/current byte/function/call/data ledgers and complete selected windows, actual v1.44/v1.52 tool/SDK/dependency gates, isolated immutable harness inputs, all raw receipts/logs/signature/effect assertions and previous failures. Initial controlfd733 failed before compiler on missing transitive analyze.py; that actual failure remains immutable. Separately reviewed dabc fixed helper import closure, used a fresh output and compiled once. Runtime45f adds no fixture/probe/build; runtime source/candidate metadata rebindings are explicit, and archived e0 versus actual bb helper explicit-v1.44 equivalence is separately proved. Scratch evidence is not a main build/current selection by itself.

<details>
<summary>Historical accepted3ae checkpoint and inherited recovery history</summary>

# Pump: five CTO owned-error restorations

Tested scratch candidate `3ae5bb44a614ae083900ca6825fa91946f475457524c1d321e06cf3724555191` (1,582,896 bytes) restores named owned AnchorError construction for existing CTO guards6084,6090,6089,6077,6078. Predicates/order, typed BondingCurve and accepted mutation/borrow/CPI/Clock behavior remain unchanged. Six unresolved numeric-return occurrences remain unchanged;6030/2006 require compared-pubkey ownership, and6019/6091/6092 need further attribution.

Existing changed-guard differential/signed coverage:6084 2/1;6090 4/1;6089 6/1;6077 1/0;6078 9/1. Exact original names/messages are observed on22differential and4signed cases. Current source origins remain truthful and differ from historical coordinates. These finite checks do not prove allocation-failure behavior, every error/cleanup path or whole original byte identity.

Evidence: [`repro/pump/admin-cto-error-batch-fortyeight`](../../repro/pump/admin-cto-error-batch-fortyeight/README.md). The packet preserves exactsource37, full original/current function/call/data/raw residual ledgers, explicitv1.44 compile/v1.52 strip, actual current orchestration hashes, dependency/tool/SDK gates and unchanged9269+1024 receipts/signatures. Initial preparation failed before VM on a pass21 CI-only provenancehash; root approved the exact hash after retaining old/current bytes/maps/diff. No replaygenerator/assertion/fixture changed, no runtime retries or new probes.

<details>
<summary>Historical ffa checkpoint and inherited recovery history</summary>

# Pump: owned holder-downgrade error checkpoint

The tested scratch executable is `ffa0f3bab34b8cfca6d6aeef5e6b8dcabad0a16eccfeb3d22d5781e22ae3b193` (1,581,624 bytes). One existing admin-CTO holder-downgrade guard now returns the named `HolderRewardCreatorImmutable` Anchor error instead of `ProgramError::Custom(6083)`. Its predicate/order, the accepted owned6088/6080 guards, typed full BondingCurve and scoped borrow/mutation/CPI/Clock ordering remain unchanged.

The error number, name and message match original on six existing differential cases. No existing signed Surfpool case reaches6083; signed changed-guard coverage remains zero. Source origins remain truthful and differ: original `programs/pump/src/creator/admin_cto.rs:289`, recovered `src/admin_cto.rs:103`. No padding, remapping or historical-coordinate constants are used. Whole original application/executable bytes remain unmatched; other numeric guards and allocation-failure behavior remain unresolved.

The evidence package is [`repro/pump/admin-cto-owned6083-fortyeight`](../../repro/pump/admin-cto-owned6083-fortyeight/README.md). It binds the exact one-file patch, all 37 source inputs, pinned v1.44 compile/v1.52 strip tools, SDK/helpers and 252 package/14,281 file dependency gates; full original/current functions/calls/data and byte residuals; and unchanged finite comparison/signature receipts. No new fixture/probe was added. The previous recovery history and prior coverage limitations remain below.

<details>
<summary>Historical accepted c261 checkpoint and inherited recovery history</summary>

# Pump: owned admin-CTO error checkpoint

The tested scratch executable is `c261d215495a35aa59970546b87bd5fb74407d2bbd5d885d41a0d1a2677cc2f2` (1,581,232 bytes). It changes one admin-CTO guard from a generic `ProgramError::Custom(6088)` to the existing named `CtoNotAllowedForMayhemCoin` Anchor error. The typed BondingCurve parser, accepted mutation/Clock/CPI ordering and scoped borrow repair are retained.

The original and candidate now produce the same error number, name and message on the existing covered 6088 cases. Their source origins intentionally differ: original `programs/pump/src/creator/admin_cto.rs:284`; recovered source `src/admin_cto.rs:103`. No historical source coordinates, compiler layouts or byte identity are fabricated.

The immutable scratch evidence is [`repro/pump/admin-cto-owned-fortyeight`](../../repro/pump/admin-cto-owned-fortyeight/README.md). It retains the one-file source patch, pinned v1.44 compile/v1.52 strip controls, all 37 input hashes and 252 package/14,281 file dependency gates, complete original/current function and call/data ledgers, and unchanged regression/signature receipts. Whole original executable and application byte identity remain false.

Finite validation: 9,269 unchanged differential comparisons and 1,024 unchanged signed Surfpool comparisons. The changed guard is covered by two existing differential cases and one existing signed case; this does not establish all error/cleanup/allocation-failure behavior. Other numeric guards remain unresolved. Prior cashback/6080 and exact 123-byte nonzero-fee coverage limitations remain as documented below. No new fixture or probe was added.

<details>
<summary>Historical accepted 5d checkpoint and inherited recovery history</summary>

# Pump admin-CTO typed-curve checkpoint

The current tested executable is **1,580,712 bytes**, SHA256 `5d35884bf79de90850e23ac5e6781b328430b8748f62e4c1381cb77b9f2e0a6c`. Root's clean main build matches the complete tested scratch executable and unstripped symbol file (`9f74f5cf77c959999064695c046a41b70c497db02d98e80742eb11edc2c34305`). See the [main identity record](../../repro/pump/admin-cto-typed-main-fortyeight/main/controls/identity.json) and [scratch evidence](../../repro/pump/admin-cto-typed-fortyeight/README.md).

This checkpoint changes only `admin_cto.rs`: it uses the recovered full BondingCurve account, writes decoded fields before the pool-update CPI and AdminCto Clock/event, clears cashback when selecting holder mode, and restores the creator-fee/cashback 6080 guard. The first scratch compile failed on a borrow-scope conflict; the reviewed borrow-only repair compiled successfully. Both attempts are retained. No compiler or layout variant was used.

All **9,269 unchanged differential comparisons** and **1,024 unchanged Surfpool comparisons** passed, with saved signature/effect verification. The CTO-specific 363 differential and 24 Surfpool cases passed. They do not exercise holder mode with an already-cashback curve, the restored 6080 error, or an exact 123-byte curve with a nonzero partial fee field; those refinements remain supported by static source/CFG evidence, not direct runtime coverage.

The 48 bounded-handler disposition is unchanged. Five partial paths, stopped scopes, incomplete error/indirect/data reconstruction, unknown historical build provenance and incomplete security assessment remain. Whole original ELF identity is false. Earlier buy/creator evidence below remains useful history but its older executable hashes, sizes and function counts are not the current checkpoint.

<details>
<summary>Historical buy and creator notes — verbatim frozen scratch README proposal</summary>

# Pump buy fee basis and validation order

This checkpoint retains48 bounded handlers and five partial paths. The prior pretrade market-cap correction remains in `buy_v3` and `buy_exact_quote_in_v3`: ordinary mode reads the parsed mint supply; Mayhem mode reads `BondingCurve.token_total_supply`. A natural zero-base6026 guard precedes that selection. The admitted buy_v3 path now rejects complete curves before cashback curves, preserving original6005 precedence when both flags are set. buy_exact_quote validation order remains unchanged. No whitelist exemption, reserve/reload continuation or sell behavior is added.

The tested isolated executable is1,588,408 bytes, SHA256 `bc6775052d8d335907d2a797113a4bb8e0008f07fa9d69c7597984fda9887314`. It does not equal the captured original. Any main build must independently establish entire stripped and unstripped identity before carrying these receipts to main.

The full original cap helper and emitted helper remain760 bytes each but differ in code ordering, calls/data and diagnostic origin. The new validation-order source change produces nine differing executable bytes relative to the previous checkpoint, all within the full buy body; the exact_quote body remains raw-identical. The complete fresh inventory retains1035 original windows and789 candidate windows,454/427 call-consistent matches and617 raw-equal pairs. No normalized or partial match is asserted as whole-file identity.

The unchanged9269 differential comparisons and1024 Surfpool comparisons are preservation obligations for this checkpoint; saved receipts and their verification outcome reside in the source-build evidence package. The direct V3 fixture uses equal mint and curve supplies of10^15, and does not validate divergent-supply behavior. Existing cases also do not establish coverage of both complete and cashback flags reaching the reordered buy checks; passing regressions are preservation evidence. No new test case, signer workaround or compiler experiment is included.

Original typed FeeConfig admission and whitelist's four-zero bypass remain unintegrated in the current unchecked/late-decoded fee path. Broader buy settlement/error order, volume, events, original source/build provenance and full security assessment remain incomplete. All stopped scopes remain stopped.

Earlier full recovery history remains in the [connected decoder/preparation README](../../repro/pump/curve-preparation-fortyeight/README.md) and the [active fee-basis checkpoint README](../../repro/pump/buy-fee-basis-fortyeight/README.md). Those immutable reports retain their original source, runtime and provenance limitations.

Creator contexts now use the recovered full BondingCurve decoder/serializer instead of partial166-byte buffers. Migration captures its old/new creator keys and mutates creator before Clock/event construction; setter/sync preserve the original early-return logs. The isolated creator-full-curve checkpoint remains a bounded reconstruction and preserves prior fee/admission/settlement limitations. See the [creator source/build report](../../repro/pump/creator-full-curve-fortyeight/README.md) for exact tested artifact and coverage.

AdminCto now uses the recovered full BondingCurve account model, updates decoded fields before the pool-update CPI and restores the original holder/cashback and creator-fee guard behavior. The [admin-CTO typed checkpoint](../../repro/pump/admin-cto-typed-fortyeight/README.md) retains the source proof, initial borrow-check failure, reviewed scope repair and final finite validation. Earlier creator, fee/admission and settlement limitations remain in the linked checkpoint history.

The unchanged CTO corpus does not exercise holder mode with an already-cashback curve, the restored6080 error, or an exact123-byte curve containing a nonzero partial fee field. Those refinements are supported by the retained static source/CFG proof, not direct runtime coverage.

</details>

</details>

</details>

Recorded integrity limit: both differential and Surfpool orchestrators exited1 at their final global check because the build helper changed concurrently. All target child suites exited0 and saved signatures/effects passed. The frozen build passed old-helper before/after gates. Root-reviewed explicit-version AST equivalence proof seal `eb9173e77c85d1b5e55c8556b52e002ad655e5abe3b8a430a13e5a7fe7cb3223` admits only exact old→current helper transition with explicit nonempty v1.44/v1.52; all other inputs were rechecked. This is not a blanket whole-integrity PASS; no runtime rerun occurred.

</details>

</details>

</details>
