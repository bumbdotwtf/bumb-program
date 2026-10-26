# PumpSwap source reconstruction

The selected checkpoint is [collect owner6048](../../repro/pump_amm/owner6048-v144/README.md), executable `09bee0dfd751dc6ae0240bbac262933c6bda6e0c94aa643f82c57f2956c3a117`. A genuine managed-source build reproduced the independently tested executable and symbols. The plain require preserves the owner predicate and error6048 while removing unsupported compared-key decoration; the current source origin is truthful `src/collect.rs:20`.

The unchanged corpus retains 17,462 cases, 35,074 submissions and 35,418 verified signature fields. Existing owner-error fixtures do not assert strict compared-key/origin diagnostics, and original parser-versus-handler attribution remains unproved. Whole-original byte equality is false; 297 original windows remain unmatched. Opaque pointer/callee behavior, generic stack safety, complete source/build provenance and exhaustive behavior/security acceptance remain open.

## Prior checkpoint documentation

The following text describes earlier checkpoints and remains preserved as historical evidence.

# Partial PumpSwap source recovery

Thirty-seven of 38 published handlers have bounded runtime validation from
captured-program behavior and disassembly, including legacy buy, exact-quote buy,
sell, direct fee/cashback payouts, boost buy-and-burn, and AMM/curve multi-hop routes.
The remaining `create_config` source is reconstructed and compiled with static-only
evidence; no authentic successful fixed-administrator initialization replay exists.
It is excluded from the 37-handler runtime count. This is not a replacement for
the deployed program and does not match its bytes.

```sh
work/test-env/bin/python scripts/prepare_locked_cargo_home.py \
  --lockfile programs/pump-amm/Cargo.lock --output work/amm-replay-cargo-home
CARGO_HOME="$PWD/work/amm-replay-cargo-home" work/test-env/bin/python scripts/build_partial_candidate.py \
  --manifest programs/pump-amm/Cargo.toml --program pump_amm \
  --artifact-name pump_amm_recovered.so --tools-version v1.44 \
  --extra-input programs/pump-amm/vendor/solana-pubkey --output work/amm-replay-build
work/test-env/bin/python scripts/pump_amm_admin_differential.py \
  --candidate work/amm-replay-build/artifacts/pump_amm_recovered.so \
  --output work/amm-replay-admin.json
```

The v1.44 checkpoint uses a pinned, checksum-verified dependency graph and a clean
main-path build. The previous v1.52 cashback checkpoint remains preserved. Both
the compiler and lockfile changed, so this is not a compiler-only experiment or
proof of the historical compiler/dependencies. The preceding 32-handler compiler checkpoint is preserved. See
[`repro/pump_amm/compiler-v144`](../../repro/pump_amm/compiler-v144/README.md) and
[`audit/pump_amm/COMPILER_V144.md`](../../audit/pump_amm/COMPILER_V144.md) for full
build provenance, artifact identity and limits. Cache preparation requires the
pinned archives to be locally available; it does not download them.

The legacy buy checkpoint adds two bodies and corrects zero-fee cashback sell event
labels. All 23 suites pass 16,221 comparisons, including all previous cases, 16 sell
regressions, and 1,011 buy/exact-quote cases. Its clean main-path build uses the same
v1.44 lockfile. See
[`repro/pump_amm/legacy-buy-thirty-five`](../../repro/pump_amm/legacy-buy-thirty-five/README.md)
and [`audit/pump_amm/LEGACY_BUY_RECOVERY.md`](../../audit/pump_amm/LEGACY_BUY_RECOVERY.md).
The previous AMM33 package and its subsequently discovered negative event receipt
remain preserved; the new package binds that exact signed case to a passing regression.

The boost buy-and-burn checkpoint adds one body. All 24 suites pass 16,727
comparisons, including 506 new normally signed boost cases. Its clean main build
is identical to the scratch executable used for the complete regression run.
Quote transfer, base burn, trade/boost events, final vault closure, Token-2022 fee
harvesting, and error 6088 are covered by the bounded corpus. See
[`repro/pump_amm/boost-burn-thirty-six`](../../repro/pump_amm/boost-burn-thirty-six/README.md)
and [`audit/pump_amm/BOOST_BUY_BURN_RECOVERY.md`](../../audit/pump_amm/BOOST_BUY_BURN_RECOVERY.md).
The earlier AMM35 package remains immutable.

The multi-hop checkpoint adds one body. All 25 suites pass 17,462 comparisons,
including 735 new normally signed route cases. The clean main-path executable
matches the scratch executable exactly; the maintained route harness also passes
from `/tmp`. One, two and three AMM legs, grouped Pump curves, both kinds of
AMM/curve transition, inline fee allocation, captured CPIs, rollback/error order,
and endpoint/intermediate token transfer fees are covered. See
[`repro/pump_amm/multi-hop-thirty-seven`](../../repro/pump_amm/multi-hop-thirty-seven/README.md)
and [`audit/pump_amm/MULTI_HOP_RECOVERY.md`](../../audit/pump_amm/MULTI_HOP_RECOVERY.md).
Earlier packages remain immutable. Fixed-admin `create_config` remains static-only:
retained runtime evidence consists of 372 ordinary-signer rejection comparisons,
with no successful fixed-administrator initialization replay. No signer bypass is used.

Additional SBF suites are `scripts/pump_amm_buyback_differential.py`,
`scripts/pump_amm_fee_config_differential.py`,
`scripts/pump_amm_resize_differential.py --creator`, and
`scripts/pump_amm_reserved_differential.py`, and
`scripts/pump_amm_accumulator_differential.py`, and
`scripts/pump_amm_liquidity_differential.py`, and
`scripts/pump_amm_trade_v2_differential.py`,
`scripts/pump_amm_create_differential.py`, and
`scripts/pump_amm_migration_create_differential.py`, and
`scripts/pump_amm_boost_differential.py`, and
`scripts/pump_amm_sweep_differential.py`, and
`scripts/pump_amm_extend_differential.py`,
`scripts/pump_amm_collect_differential.py`, and
`scripts/pump_amm_transfer_creator_differential.py`,
`scripts/pump_amm_creator_reassignment_differential.py`, and
`scripts/pump_amm_creator_reassignment_cto_differential.py`, and
`scripts/pump_amm_incentives_differential.py --family sync|admin|claim`, and
`scripts/pump_amm_cashback_differential.py`, and
`scripts/pump_amm_legacy_sell_differential.py`, and
`scripts/pump_amm_legacy_buy_differential.py`, and
`scripts/pump_amm_boost_burn_differential.py`, and
`scripts/pump_amm_multi_hop_differential.py`, each taking `--candidate` and `--output`.

For a clean build with complete source/lock/toolchain hashes and an unmodified
whole-file comparison, use `scripts/build_partial_candidate.py`. See
`audit/pump_amm/ADMIN_RECOVERY.md` and `audit/pump_amm/LIQUIDITY_RECOVERY.md` and
`audit/pump_amm/TRADE_V2_RECOVERY.md` and `audit/pump_amm/CREATE_POOL_RECOVERY.md` and `audit/pump_amm/BOOST_RECOVERY.md` and `audit/pump_amm/SWEEP_RECOVERY.md` and `audit/pump_amm/EXTEND_RECOVERY.md` and `audit/pump_amm/CREATOR_FEES_RECOVERY.md` and `audit/pump_amm/CREATOR_REASSIGNMENT_RECOVERY.md` and `audit/pump_amm/INCENTIVES_RECOVERY.md` and `audit/pump_amm/CASHBACK_RECOVERY.md` for recovered constraints and limitations.

The preceding [Pool serializer checkpoint](../../repro/pump_amm/pool-serialization-thirty-seven/README.md) preserves those 37 bodies and reruns all 25 suites / 17,462 comparisons. Both Pool and GlobalConfig complete normalized account-exit bodies match the captured original, including each exit's 24 direct call targets. Its clean main and scratch executables are byte-identical; equality to the original whole binary remains false. The prior [GlobalConfig checkpoint](../../repro/pump_amm/serialization-thirty-seven/README.md) remains preserved. See [the Pool serialization audit](../../audit/pump_amm/POOL_SERIALIZATION_RECOVERY.md) for the source correction and verification limits. At that checkpoint, static-only `create_config` source was retained separately and was not promoted.


The preceding [scalar guard-order checkpoint](../../repro/pump_amm/scalar-guard-order-v144/README.md)
restores `update_fee_config` scalar compared-value diagnostics and the original
LP → protocol → recipients → creator guard/store order. The unchanged 25-suite
corpus passes all 17,462 comparisons; stricter Left/Right assertions pass on 191
existing scalar-fee rejection cases. There are no added handlers or test cases.
The clean main executable is byte-identical to the tested scratch executable;
35,418 signatures are verified, with 150 existing setup transactions accounted
for separately from comparison cases. The complete Pool and GlobalConfig exit
matches and their 24 direct targets each are rechecked at the new candidate locations.

At that checkpoint, the fee-config handler remained structurally unmatched: 6,096 candidate bytes versus
2,912 original bytes, with no standalone 616-byte scalar-setter match. Its actual
error helper retains constant-specialization differences. Compilation uses pinned
v1.44 and the unchanged installed SDK performs its separate v1.52 strip phase;
these are recorded as separate tool identities. Whole-file equality and the audit
remain incomplete. Earlier checkpoints and failed evidence checks remain preserved.


The preceding [create-config/shared-method checkpoint](../../repro/pump_amm/create-config-shared-methods-v144/README.md)
adds the reconstructed initializer/context/event source and shares the four original
GlobalConfig methods between creation and fee updates. The fixed administrator,
Signer requirement, canonical config/event PDA constraints, System CPI ordering
and event/exit ordering are preserved. Creation remains static-only: this checkpoint
adds no positive initializer execution, bounded handler count or test case.

All 25 unchanged suites pass 17,462 comparisons on its executable. Saved-evidence
checks verify 35,418 signatures, including 150 existing setup transactions counted
separately, and stricter diagnostics on 191 scalar and 78 recipient rejection cases.
The recipient method restores the original plain error output without spurious
Left/Right public-key diagnostics. Its clean main build is bound to the tested
scratch corpus through complete ELF identity, with all 22 actual inputs recorded.

The complete create wrapper, handler, account parser and event serializer match
original normalized instruction bodies. The init helper and recipient setter retain
truthful source-coordinate differences; their immediate callees match completely.
Three scalar methods remain 608 bytes versus 616 original bytes. The fee-update
handler is 3,160 bytes versus 2,912 original bytes, and its actual scalar error helper
retains four specialization differences. The genuine two-caller graph alone does
not reproduce the original code generation. Eleven compiler panic/format/I/O data
references remain outside complete recursive data verification.

The complete Pool and GlobalConfig exits, all 24 direct targets each and their
discriminators still match at this candidate's fresh symbol locations. Compilation
uses pinned v1.44; the unchanged installed SDK's separate v1.52 strip phase is
recorded independently. Whole-file equality and the audit remain incomplete.
All earlier checkpoints and negative evidence remain immutable.


The preceding [event-borrow checkpoint](../../repro/pump_amm/update-event-borrow-v144/README.md)
removes only the redundant clone passed to `emit!` in `update_fee_config`.
The handler now measures 2,912 bytes and its complete normalized instruction body
matches the captured original. The 2,296-byte wrapper and 744-byte event serializer
also match. This is source-derived output from the unchanged pinned build recipe.

All 25 unchanged suites passed 17,462 comparisons on the exact scratch executable.
The clean 22-input main build has complete ELF identity with that executable,
justifying receipt reuse without another replay. Saved checks verify 35,418
signatures, 191 scalar and 78 recipient diagnostics; the 150 existing setup
transactions remain separate from comparison cases. No handler or case is added.

The handler's immediate target closure remains 12 of 16: three scalar methods
remain 608 bytes versus 616 original bytes, and the recipient setter retains
truthful source-coordinate differences. The actual scalar error helper still has
four specialization differences. Five bounded update data references and both
inline event constants match; four compiler metadata references remain unclosed.
The initializer retains all previous static limits and has no authentic successful
runtime replay. The complete Pool and GlobalConfig exits, their 24 direct targets
each and discriminators still match at fresh symbols. Compilation uses v1.44 and
the unchanged SDK separately strips with v1.52. Whole-original ELF equality is
false, and the audit remains incomplete. Earlier packages and seals stay immutable.


## Destination rent checkpoint

The preceding AMM is the [destination-rent checkpoint](../../repro/pump_amm/destination-rent-v144/README.md) (`2a8a69f1…`, 1,199,064 bytes). The main executable and symbol ELF equal the reviewed scratch candidate. The one-line correction uses the destination account data length for rent. All 17,462 existing comparisons and 35,418 saved signature checks are retained; no new fixture or main replay is claimed. Pool and GlobalConfig complete normalized serializers, each of their 24 direct targets and discriminators match. The complete 2,912-byte fee-update handler, wrapper and event serializer still match under normalization; 12/16 immediate handler targets match. Scalar methods, recipient source coordinates and transitive data remain unresolved. Initializer static matches remain, but authentic successful replay is absent. The 267 transfer rows include zero-lamport destination-data cases and do not validate live nonempty accounts; the external 8/267 claim remains unverified.


## Accumulator mutation ordering checkpoint

The [accumulator-order checkpoint](../../repro/pump_amm/accumulator-order-v144/README.md) moves only the user-field assignment in `init_user_volume_accumulator` after successful `Clock::get()`, matching the original instruction order. The isolated executable is `8ce5f958…` (1,199,072 bytes). The 25 unchanged suites passed 17,462 comparisons; saved evidence verifies 35,418 signatures, including the 150 existing setup transactions. No case or initializer-success fixture was added. The complete before/after inventory remains at 785 original and 653 candidate windows, with 310 original windows unmatched. The source-order improvement does not establish a committed-state difference on a reverted transaction, historical source spelling, transitive closure, or whole ELF identity.


## Restored base58 formatter

The [formatter-restoration checkpoint](../../repro/pump_amm/formatter-restoration-v144/README.md)
restores the stack-buffer base58 algorithm and checked UTF-8 conversion supported by
the original renderer. The complete solana-pubkey 2.4.0 archive is vendored with
only the reviewed formatter/import and bs58 dependency changes. Package versions
and all other lockfile records remain unchanged; the original dependency revision
is still unresolved. Third-party attribution is in THIRD_PARTY_NOTICES.md.

The clean main executable and symbol ELF exactly equal the tested scratch build.
The executable is 1,196,544 bytes, SHA256
`d3dacf1bd54e0b7b825557d01adfe158bc229753fb4b945618c5eabf2bdb1bab`.
All 25 unchanged suites passed 17,462 comparisons; saved checks verify 35,418
signatures. Four additional original function windows match under the existing
normalization, including the entire 1,520-byte renderer and its ten immediate
target bodies. There remain 306 unmatched original windows. Raw binary equality,
recursive data and indirect-call closure, authentic initializer success and the
security audit remain incomplete. Diagnostic source locations remain truthful.


## Claim account ownership checkpoint

The [claim-context checkpoint](../../repro/pump_amm/claim-context-v144/README.md)
restores owned `AccountInfo` values for the claim user and event authority, and
stores the global accumulator `Account` inline. Complete constructor, member and
drop evidence supports these three declaration changes. The clean main executable
and symbol ELF equal the tested scratch build; the executable SHA256 is
`6f2589487eac44be02788312a55bcba09cebea635d9bdf0880d65b9999381815`.

The 25 unchanged suites passed 17,462 comparisons and saved verification checked
35,418 signatures. Four more original windows now match normalized bodies: the
claim parser, initializer closure, exit and wrapper. There remain 302 unmatched
original windows. Parser recursive graph correspondence and the wrapper's handler
target remain unresolved; normalized wrapper instructions do not prove transitive
equivalence. No new runtime case or initializer-success fixture was added. Full
original ELF identity and broader reconstruction obligations remain open.


## Claim overflow ordering checkpoint

The [overflow-order checkpoint](../../repro/pump_amm/claim-overflow-order-v144/README.md)
computes the new claimed total before clearing unclaimed rewards. Static evidence
shows the original rejects addition overflow before accumulator mutation, and the
compiled correction restores that order. The clean main executable and symbol ELF
equal the tested scratch build. Its executable SHA256 is
`eeca5a51c40489452a71b698e7d7ff5bf3cc6c5002659807133907a4cb5eb5e8`.

All 25 unchanged suites passed 17,462 comparisons; saved checks verify 35,418
signatures. No new case, probe or compiler variant was added. The full inventory
remains at 483 normalized original matches and 302 unmatched original windows.
The claim handler remains a mismatch, and no persisted-state difference is claimed
for transaction rollback. Whole original ELF equality remains unresolved.


## Claim self-transfer admission checkpoint

The [self-transfer checkpoint](../../repro/pump_amm/claim-self-transfer-v144/README.md)
restores the original application predicate before Claim's token CPI: different
source/destination addresses pass; equal addresses require the source token owner
to equal the global accumulator authority. The compiled candidate includes the
plain SelfTransferNotAllowed error and retains the same downstream SPL helper.
The clean main executable and symbol ELF equal the tested scratch build;
executable SHA256 is
`ad74b08447914cb219624f9e9cc81d4cfe751b332d67534c45aec63ef70aa166`.

All 25 unchanged suites passed 17,462 comparisons, with 35,418 saved signatures
verified. No new fixture or probe establishes failure reachability: the existing
ATA parser constraints may already exclude this error for admitted Claim inputs.
The complete inventory remains at 483 normalized original matches and 302
unmatched windows. The whole handler, recursive call/data closure and original
ELF identity remain unresolved.


## Sync account ownership and no-change log checkpoint

The [Sync context checkpoint](../../repro/pump_amm/sync-context-v144/README.md)
restores the owned user AccountInfo and inline global accumulator Account. The
[no-change log checkpoint](../../repro/pump_amm/sync-nochange-log-v144/README.md)
then restores the original formatted user message when Sync makes no change.
Both independent scratch proofs and the cumulative main build are retained.
The main executable and symbol ELF exactly equal the final tested scratch;
executable SHA256 is
`c96ed810bccdcc741ab811c846a2ad76bd50163c4f635ef3a61db6562114d69c`.

All 25 unchanged suites passed 17,462 comparisons and 35,418 saved signatures.
All 113 existing no-change message cases now match exactly; no new fixture or
probe was added. Claim source is unchanged, but the two added lines move its
SelfTransferNotAllowed diagnostic line from 147 to 149. That exact emitted
instruction difference remains explicit. Sync parser and wrapper match normalized
original bodies; its handler and recursive data/call closure remain unresolved.
The full inventory has 485 normalized original matches and 300 unmatched windows;
whole original ELF identity is not established.


## Initializer user AccountInfo ownership checkpoint

The [initializer ownership checkpoint](../../repro/pump_amm/init-user-ownership-v144/README.md)
restores the original owned `AccountInfo` for the initializer user, including its
reference counts and cleanup. The complete initializer parser, wrapper and handler
now match original normalized instructions and relocation patterns. The tested
scratch executable SHA256 is
`3fe52eea99e26866795348aad93fb821f834bf04290b4176a67ae0b7add0fcb5`.

The unchanged 25 suites passed 17,462 cases and 35,418 saved signatures; all 113
existing Sync no-change messages still match. No new initializer-success fixture
was added. The full inventory has 488 normalized original matches and 297
unmatched windows. The initializer's nested helper remains mismatched; full
callee/data and original ELF equality remain unresolved. Close, Sync and Claim
bodies are unchanged from the preceding checkpoint, including the known Claim
diagnostic line 147 to 149 difference. Main acceptance requires the separate
[main identity companion](../../repro/pump_amm/init-user-ownership-main-v144/README.md).


## Initializer logical-module checkpoint

The [logical-module checkpoint](../../repro/pump_amm/init-logical-module-v144/README.md)
places only the initializer Accounts context into its evidenced instruction-file
hierarchy and re-exports it. Fields, constraints and the handler remain unchanged.
The tested scratch executable SHA256 is
`6dc621c8c6a165650a159b67f9f2d042c3ffc71481236208d2565485c3e169b2`.

The natural emitted filename has length65 and line4; the original has length83
and line8. No workspace, remap, padding or flag change was used. The full inventory
retains488 normalized original matches and297 unmatched windows, with zero gains
or losses. All25 unchanged suites pass17462 cases and35418 saved signatures;
all113 existing Sync messages remain exact. No new initializer-success fixture
or whole-byte-match improvement is claimed. The separate
[main companion](../../repro/pump_amm/init-logical-module-main-v144/README.md)
binds a clean main build to the tested scratch. Original root/workspace provenance,
remaining helper metadata and recursive call/data identity remain unresolved.
