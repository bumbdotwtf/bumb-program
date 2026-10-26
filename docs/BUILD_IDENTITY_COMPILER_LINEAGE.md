# Direct compiler-lineage and SDK evidence

This update supplements the [original audit](BUILD_IDENTITY_AUDIT.md) and [backend/provenance follow-ups](BUILD_IDENTITY_AUDIT_FOLLOWUPS.md). The accepted application source, status and artifacts have not been promoted by these experiments. Original-byte identity remains **0/4 core programs and 2/5 dependency payloads**. A measured library family is not a complete historical build recipe.

## Pump and PumpSwap have independent v1.44 evidence

The [direct two-capture comparison](../repro/core-library-family/REPORT.md) closes the earlier qualification that Pump/AMM were borrowing Fees' compiler evidence. Both original captures independently contain v1.44's complete raw-exact 1,056-byte `fmt::write` and 352-byte multiply leaf. The full Unicode 872/712-byte consumer/check pair, its actual call, six full arrays totaling 1,403 bytes and their caller/callee extent arguments also match under the stated instruction/relocation method.

Stock v1.43, v1.45, v1.46 and v1.46.1 retained recipes have negative complete named-function results in both captures. These are measured recipe negatives, not exclusion of all custom profiles or mixed pipelines. No new compiler build or transaction was needed. Indirect formatter data, panic/global-data closure and complete application code remain open. Together with Fees' prior independent measurements, v1.44 is the strongest measured stock family for these three older core captures. Mayhem's separate v1.54 evidence must not be transferred to them.

## Relay's scratch buffer distinguishes v1.48 from v1.47

The [static owning-source proof](../repro/donation-relay/sort-scratch-compiler-discriminator/REPORT.md) found that the original 608-byte helper and stockv1.47 candidate differed in six non-relocated scratch operands, two actual call displacements and one loader-relocated pointer. The authentic explanation is [Anza Rust commit 7d0f408](https://github.com/anza-xyz/rust/commit/7d0f408143f58488e328dff76241983d5f749e1f), included in the next official platform-tools release v1.48. It selects 2,048-byte scratch for the Solana family without dynamic frames; v1.47 always selected 4,096 in this path.

A [single v1.48 measurement](../repro/donation-relay/source-build-12-v148-measurement/REPORT.md) compiled the exact same 23 frozen Relay inputs and 232-package lock, with the original profile, remap flag and fixed strip phase. No application source, metadata, profile, feature or dependency override was tried. The actual compiler cfg declares Solana family, genericV0, no dynamic frames. Both compiler and strip returned zero.

| Discriminator | Original Relay | Frozen source/v1.47 | Frozen source/v1.48 |
| --- | ---: | ---: | ---: |
| Sort scratch bytes |2,048|4,096|2,048|
| Passed scratch element capacity |85|170|85|
| Lowest direct r10 displacement in this helper |−2,064|−4,112|−2,064|
| Full 608-byte instruction/relocation correspondence |reference|negative|positive|
| Compiler backend error lines |not a build receipt|2|0|

The v1.48 helper retains raw differences in actual call/pointer immediates; it is **not raw-identical**. The offset 160 multiply edge is independently closed through the named 72→352-byte proof; the other reached callees are checked by the retained matcher. This does not close indirect/transitive behavior or all referenced data. The corresponding formatter 1,128-byte raw positive, full Unicode 696→704-byte pair/all 1,449 table bytes and resolved multiply chain persist.

The v1.48 artifact is 501,144 bytes, SHA-256 `6c32f830015bc52a890264041c20c74441db651d8f6efd6558d8fa13adec1783`; whole Relay identity remains false. Its full ledger has 57 raw/225 instruction-pattern matches and 267 unmatched original windows. v1.47 had 59/224/268. These layout-dependent counts are not a monotone recovery score or source percentage. Original profile/source organization, application ABI, ownership/error/cleanup, indirect calls and data remain unresolved.

The saved v1.48 scan finds no direct frame-displacement starts outside its tested interval. That scan does **not** establish access-width/end-crossing safety, derived-pointer safety, call-stack safety, runtime acceptance or all-state equivalence. Likewise, 3,857 authenticated files means members under 152 observed compiled registry roots; the receipt does not prove rustc opened every member. No VM, SDK execution or accepted-artifact promotion occurred. Later releases/custom sysroots remain possible, so there is no unique historical-version claim.

### A genuine distribution-data discrepancy remains

At the helper's data reference, the capacity-error path carries a pointer toward the panic pipeline, ending at external `custom_panic`. A bounded first 24-byte Location-shaped observation has source position 915:9 and a pointed 84-byte `/Users/runner/work/platform-tools/platform-tools/out/rust/library/alloc/src/slice.rs` string in the Darwin candidate, versus 83-byte `/home/runner/work/platform-tools/platform-tools/out/rust/library/alloc/src/slice.rs` in the original. Full referenced-object extent and consumer closure are unproved; the 64-byte prefix includes adjacent records.

This supports inspecting the authentic Linux distribution's library data next. It does not prove the original compiler host uniquely, justify path/coordinate fabrication, or establish a Linux build before it is measured. The current distribution was downloaded from the official release and sealed, but its publisher digest field is null. That distinction remains explicit.

## ATA's exact swapped types and ordering mechanism are now attributed

The [static monomorphization-order packet](../repro/ata/monomorph-order-proof/REPORT.md) identifies the exchanged bodies as `RawVec<u8, Global>` and `RawVec<AccountMeta, Global>`. Complete retained object bodies and actual named caller relocations distinguish the types; equal body sizes alone do not. Native and Linux controls independently support the attribution. These controls are not an unstripped best candidate2.

Authentic Rust/Cargo owning sources establish how unit metadata and type identities feed generic symbol hashes, then same-definition monomorphization ordering. The original stripped capture retains neither internal mangled names nor rustc/debug metadata. Original uploader invocations, unit graph and corresponding unstripped object/rmeta remain missing. In particular, Cargo fingerprint JSON's `metadata` integer hashes manifest descriptive fields; it is **not** recovered `-Cmetadata`. No arbitrary metadata override or new ATA build was attempted. The 307-position residual is unchanged.

## SDK literal routes and declaration coverage

The [action/account matrix](../repro/sdk/action-account-matrix-20261025/REPORT.md) exhausts 104 literal builder sites and 71 distinct program/instruction routes within the authenticated shipped SDK sources. It lists all 124 bundled instruction declarations and 1,134 ordered account rows. An independent frozen Rust comparison agrees in account order and declaration-derived signer/writable/optional flags for all 121 present wrappers. The three already-known missing Pump wrappers remain. No observed caller or successful replay is not evidence that an identified original entrypoint can be removed from byte-identity scope. No new concrete active account discrepancy is established.

This is a bounded lexical/declaration audit. Twenty-five builder sites retain unresolved helper/variable account expressions; public Program factories, dynamic calls, callbacks, Anchor partial-account resolution and runtime-dependent remaining accounts are not exhaustively closed. PDA-module exports and general literal-return-object candidates are source observations, not numeric PDA/account-meta proofs. SDK dependency ranges still lack an exact resolved JavaScript dependency closure. Optional Agent Payments remains outside the archived nine-program target plan. Relevant excluded actions remain passive; no JavaScript, SDK builder, RPC or target runtime was executed.

## Recompute the new evidence

```sh
python3 -B repro/core-library-family/verify.py
python3 -B repro/donation-relay/sort-scratch-compiler-discriminator/verify.py
python3 -B repro/donation-relay/source-build-12-v148-measurement/verify.py
python3 -B repro/ata/monomorph-order-proof/verify.py --repository-root .
python3 -B repro/sdk/action-account-matrix-20261025/verify.py
```

These commands inspect saved bytes only. They do not rebuild, run transactions, resume excluded work or make the requested whole-program identity claim.
