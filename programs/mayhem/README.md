# Mayhem reconstructed candidate — measured v1.54 recipe

The tested executable is599784bytes, SHA256 ca5d4f54b14e2f67c4eca56fcac29b54801906cecf23c463801916fd9d6b6621. One genuine managed-source direct officialv1.54 Cargo/rustc build, stockgenericV0/sbpf target and fixedv1.52 strip reproduced both whole executable and unstripped symbols exactly. All14source/lock/profile bytes are unchanged. This is a measured reproduction choice; historical compiler/recipe remains unresolved. Global default frontend choices are unchanged.

The exact existing9595 comparisons (including3already-admitted two-call burn sequences) passed on this executable;15 unchanged saved receipt verifiers passed.13284retained raw transactions/26500signatures were independently verified.5906administrative executions lack raw transaction bytes. Their legacy history0 settings and unasserted constructor signature/blockhash defaults remain disclosed; trade/burn explicit true controls are unchanged. No new cases/initializer execution or bypass.

All61prior diagnostic domains remain:58raw candidate compute-consumption-line changes versus7d,3burn rows raw-identical. SDK0Ballowlist produced official warning-only results; actuallocal loader/corpus passed but decisive SDK/mainnet or whole-program equivalence is not claimed. Original777408-byte capture still differs; opaque scopes and transitive ABI/data gaps remain.

Main provenance: repro/mayhem/compiler-v154-main. Runtime: repro/mayhem/compiler-v154-runtime. Full actual frontend/source/tool/dependency/exit/postlink/function-call-data evidence is retained there.

## Historical recovery notes (archived before this recipe selection)

The inherited text below records earlier checkpoints, executable hashes, recipes and limitations. Its earlier “tested executable” and compiler references are historical; the current executable and scope are stated above. The exact prior README is also retained in documentation/README.before.md of the main packet.

# Partial Mayhem implementation recovery

This independently compiled Anchor program implements **24 of the 25 currently
identified instruction paths**. It is not a full program reconstruction, a
byte-identical ELF, or a deployable replacement. Other handlers are absent.
No original machine code is embedded or patched into the build.

Implemented paths:

- `initialize_global_params`, `initialize_fee_recipient`
- `reset_sol_deployed`, `reset_stable_deployed`, `reset_state`
- `stop_trading`, `resume_trading`
- `update_admin`, `update_trader`
- `update_max_sol_per_sweep`, `update_max_stable_per_sweep`
- `update_global_params`
- `extend_account`, `withdraw_admin`, `withdraw_quote_admin`
- `sweep_fees`, `sweep_fees_admin`
- `burn_tokens`, `sell`, `buy`, `sell_v2`, `buy_v2`
- `buy_pump_swap`, `sell_pump_swap`


## BuyPumpSwap typed sizing-error refinement

The reviewed [isolated refinement](../../repro/mayhem/buy-result-error-twentyfour/README.md)
restores the original typed `Result::unwrap` failure for a zero sizing divisor,
using `PumpSwapError::PumpSwapCpiMathOverflow` (original value11 and message).
All21 unchanged suites were replayed:9595 functional comparisons passed, with19190 recorded/derived signed
executions (not independent signature proof for every administrative receipt), with no new unique cases. The three second-burn source-location
differences remain explicit in the receipts and unchanged verifier result.
The previous extra Option-unwrap message is absent in the exercised BuyPumpSwap
zero-effective-reserve cases; source path/line and other diagnostic differences remain.
The scratch candidate is668544 bytes, SHA256
`dda5554a2faf8aa40fc86547e91c4b32c6ac44b878073dcb8bd9f7ac60b47cd4`.
Main-build acceptance, if completed, belongs to the separate
[main-promotion evidence](../../repro/mayhem/buy-result-error-main-twentyfour/README.md).
This source refinement does not recover the excluded initializer or establish
full original ELF, compiler, formatting-engine or all-input equivalence.


## SellPumpSwap typed sizing-error refinement

The reviewed [SellPumpSwap refinement](../../repro/mayhem/sell-result-error-twentyfour/README.md)
reuses the original `PumpSwapCpiMathOverflow` typed Result failure on a zero sizing
divisor. One pinned build passed the same21 suites/9595 functional comparisons,
with no new unique cases. The recorded/derived signed-execution count remains19190;
not every administrative receipt contains independently verifiable transaction bytes.
The previous extra Option-unwrapping log is absent in the exercised SellPumpSwap
zero-effective-quote cases. Source-location, compute and the three known second-burn
diagnostic differences remain explicit. The scratch candidate is668640 bytes,
SHA256 `7d416f848f03e46d9a514f4c505a8e903cdb908f52280bb961254eed90aebe1f`.
The separate [main identity package](../../repro/mayhem/sell-result-error-main-twentyfour/README.md)
records any accepted clean main build. The raw strict-guard distinction remains;
the included input-domain proof is not whole helper/ELF equivalence. The excluded
initializer and historical source/compiler recovery remain unresolved.

## Evidence and unresolved source details

The original captured binary is `evidence/original/mayhem/deployed.so`. Its
router/wrapper addresses are in `evidence/dispatch-map.json`. Account and state
recovery uses successful and failing local calls to that exact capture, supported
by its disassembly. The GlobalParams discriminator is the Anchor hash of
`account:GlobalParams`, and the serialized account length is 254 bytes.

The current source deliberately preserves unresolved field names as byte arrays
or numbered fields. The full account's Borsh positions are recovered for these
operations; historical Rust field names, numeric signedness of opaque fields,
struct memory layout, code ordering and dependency versions are not established.
The event discriminator is observed directly from original event bytes, not
claimed to derive from a recovered historical event type name.

The dependency lockfile pins an Anchor 1.0.0 candidate build. Stronger static
evidence from burn recovery supersedes the earlier 0.31.1 baseline: typed duplicate
checks, Pubkey CPI context and event-authority constants match the newer family.
Exact historical revision and dependency identity remain unresolved. The explicit
System wrapper preserves the original address-before-executable validation order.
All previous 2,953 cases still pass. The current candidate has 9,595 instruction
comparisons across twenty-one suite runs; see the [twenty-four-handler package](../../repro/mayhem/twentyfour/README.md).

## Reproduce

```sh
cargo build-sbf --manifest-path programs/mayhem/Cargo.toml --tools-version v1.52 \
  --sbf-out-dir work/mayhem-build -- --locked
python3 scripts/mayhem_validate_admin.py \
  --candidate work/mayhem-build/mayhem_recovered.so \
  --output work/mayhem-admin-validation.json
```

The 1,051 deterministic admin cases compare complete original and candidate SBF calls
inside separate LiteSVM instances. They compare instruction error, GlobalParams
bytes/owner/balance, admin and payer balance changes, logged event data, and inner
instructions. They include random valid serialized states, malformed state,
wrong owner/seeds/admin, missing/wrong accounts, signature/writability, trailing
instruction data, argument truncation, option tags, version-counter overflow,
initialization with System CPI, and event self-CPI. Full textual logs, compute
units, all transactions, and the absent instruction paths are not equivalent
claims. States are synthetic; injected configurations are not proof of reachable
mainnet states.

`repro/mayhem/twentyfour/` retains the clean build's comparison/provenance and compressed
case evidence. See `audit/mayhem/RECOVERY.md` for bounded security observations.

The additional `scripts/mayhem_validate_fee_recipient.py` suite compares 306
fee-recipient initialization cases using the exact captured SPL Token, Token2022
and ATA dependency ELFs in both VMs. It covers every u8 recipient index, native
mint/token address constraints, authorization behavior, account flags, missing
accounts and rollback after CPI. Its receipt is
`repro/mayhem/fee-recipient-differential.json.gz`.

The account-extension suite adds 301 cases and the SOL-withdrawal suite adds 274,
for 1,932 differential cases across fourteen paths. Extension cases cover account
types, size boundaries, rent funding, zero initialization, events and rollback.
Withdrawal cases cover administrator/PDA constraints, transfer errors, timestamp
updates, rate boundaries and signed-add overflow. Receipts are retained as
`extend-differential.json.gz` and `withdraw-differential.json.gz`.

Quote withdrawal adds 329 cases and the two sweep paths add 692 cases, producing
2,953 total cases across seventeen implemented paths. Both suites load the exact
captured dependency ELFs. Quote tests cover ATA creation, signed vault transfers,
rate limits and Token2022 mismatch behavior. Sweep tests cover authorization,
recipient order/duplication, counters, caps, token mutations, malformed accounts,
randomized state, arithmetic and rollback. They do not establish full program
security or equivalence outside the tested instruction/state surface.

The burn handler adds three genuine captured account families and three sequential
second-burn rejections, for 2,959 comparisons. Complete state, events, inner calls
and errors agree for those fixtures; compute logs and source locations differ.
The capture archive and portable runners are in the eighteen-handler package.

Legacy `sell` adds 396 normally signed synthetic cases: 134 successes and 262
rejections. The source preserves configured-trader authorization, typed ownership,
PDA/ATA constraints, fixed Token-2022 and self-program IDs, guard ordering,
reserve/tolerance arithmetic, the real Pump CPI, checked accounting updates,
complete 303-byte events and transaction rollback. Sell's external curve decoder
zero-pads to 141 bytes; burn retains its separate strict codec. All earlier cases
pass on the combined artifact. The main build is byte identical to the fully
tested scratch candidate, but differs from the original ELF.

```sh
python3 scripts/mayhem_sell_differential.py \
  --candidate repro/mayhem/nineteen/mayhem_recovered.so \
  --output work/mayhem-sell-replay.json
python3 scripts/verify_mayhem_sell.py \
  --candidate repro/mayhem/nineteen/mayhem_recovered.so \
  --receipts work/mayhem-sell-replay.json --output work/mayhem-sell-verification.json
```

The sell fixtures use only test-owned signatures and synthetic configuration;
they do not establish a full historical sell replay. Compute usage and recorded
source locations differ. In one zero-reserve panic case, the candidate additionally
logs an Option-unwrapping message; the error and complete rollback agree. At that checkpoint, four
other trade handlers and Mayhem-state initialization remained unrecovered.


Legacy `buy` adds 486 ordinary-signature synthetic cases: 187 successes and 299
rejections. It preserves the 23-account parser, actual 18-account Pump CPI,
price/tolerance guards, reserve-based budget and real-token cap. Actual spent SOL
and gained tokens drive checked signed-128-bit accounting. Overall and per-coin
risk checks run after the CPI, with strict upper limits; a failed check rolls back
the complete transaction. The original tests counter positivity before comparing
the low u64 limb, including for synthetic counters above u64::MAX. Complete events,
inner calls, watched account state and rollback agree with the captured original.

All 3,355 previous comparisons also pass on the combined twenty-handler artifact.
Its clean integrated-source build matches the reviewed scratch artifact byte for
byte. The portable buy harness and offline verifier can reproduce the evidence:

```sh
python3 scripts/mayhem_buy_differential.py \
  --candidate repro/mayhem/twenty/mayhem_recovered.so \
  --cases repro/mayhem/twenty/buy-cases.json --output work/mayhem-buy-replay.json
python3 scripts/verify_mayhem_buy.py \
  --candidate repro/mayhem/twenty/mayhem_recovered.so \
  --receipts work/mayhem-buy-replay.json --output work/mayhem-buy-verification.json
```

Buy fixtures use configured test-owned traders and synthetic account state, with
real program-derived CPI signing. They do not claim historical prestate or live
authority. Compute and source diagnostics differ; four panic cases retain explicit
log differences while matching failures and complete rollback. At that checkpoint, four trade paths
and Mayhem-state initialization remained absent.


Quote-aware `sell_v2` adds 1,419 ordinary-signature synthetic comparisons across
native SOL, legacy SPL Token, and Token-2022 quote families (473 each). It preserves
the 31-account parser and actual 26-account Pump CPI. The configured trader,
PDA/ATA and typed-owner constraints remain enforced. Quote selection controls the
budget cap, reserve threshold, actual received balance and global signed-i128
counter; both families share the state counter. Complete 303-byte events retain
zero native-specific fields for token quotes. All 3,841 prior comparisons pass on
the same artifact. Its clean integrated build is byte-identical to the tested
scratch build, with original executable identity still unresolved.

```sh
python3 scripts/mayhem_sell_v2_differential.py \
  --candidate repro/mayhem/twentyone/mayhem_recovered.so \
  --cases repro/mayhem/twentyone/sell-v2-cases.json --family native \
  --output work/mayhem-sell-v2-native.json
python3 scripts/verify_mayhem_sell_v2.py \
  --candidate repro/mayhem/twentyone/mayhem_recovered.so \
  --receipts work/mayhem-sell-v2-native.json --output work/mayhem-sell-v2-verification.json
```

Repeat with `--family token` and `--family token22` for the two token-quote runs.
The 418 successes and 1,001 rejections agree on full watched account state,
events, inner calls, return data and errors. Independent saved-receipt checks
verify every signature, successful quote/CPI/state/event and failed rollback.
Four panic diagnostics differ in each family, as documented in the package.
Starting business states and configured authorities are synthetic and test-owned;
no live authority or historical prestate is claimed. At that checkpoint, three trade handlers
(`buy_v2`, `buy_pump_swap`, `sell_pump_swap`) and `initialize_mayhem_state` remained absent.


Quote-aware `buy_v2` adds 1,839 ordinary-signature comparisons (613 each for native
SOL, legacy SPL Token and Token-2022 quotes), with 704 successes and 1,135
rejections. It preserves the 32-account parser, read-only global-volume acceptance,
actual 27-account Pump CPI, quote selection, reserve-based budget and real-token
cap. Checked actual-spend accounting precedes strict overall/per-coin risk limits;
rejection rolls back both Pump and Mayhem changes. All 5,260 earlier comparisons
pass on the same bytes. A clean main-source build matches the tested scratch
artifact; complete historical source or executable equality is not established.

```sh
python3 scripts/mayhem_buy_v2_differential.py \
  --candidate repro/mayhem/twentytwo/mayhem_recovered.so \
  --cases repro/mayhem/twentytwo/buy-v2-cases.json --family native \
  --output work/mayhem-buy-v2-native.json
python3 scripts/verify_mayhem_buy_v2.py \
  --candidate repro/mayhem/twentytwo/mayhem_recovered.so \
  --receipts work/mayhem-buy-v2-native.json --output work/mayhem-buy-v2-verification.json
```

Repeat with `--family token` and `--family token22`. Independent receipt checks
validate signatures, quote/CPI inputs, complete state/events, risk limits and
failed rollback. Four panic diagnostics per family remain explicitly different.
Fixtures are synthetic with configured test-owned authorities and real PDA CPI
signing. At that checkpoint, `buy_pump_swap`, `sell_pump_swap` and
`initialize_mayhem_state` remained absent.


The PumpSwap handlers add 2,496 ordinary-signature comparisons: 419 buy and 413
sell cases in each of the native, legacy-token and Token-2022 quote configurations.
Native and legacy-token quotes yield 680 successes in total; all Token-2022 quote
cases reject, matching the original fixed Tokenkeg address constraint. Buy uses
31 outer accounts and a 25-account AMM CPI; sell uses 29 and 23. Only the actual
Mayhem sol-vault PDA signs the CPI, with the configured test-owned trader signing
the outer transaction. The external Pool codec pads short data to 287 bytes;
the external GlobalConfig decoder requires its historical 418-byte prefix.

Trade sizing includes the pool's signed virtual quote reserve. Native buys fund
and synchronize WSOL, and both native trades close the quote vault afterward.
Returned rent is included in actual quote accounting, reproducing the original
small-buy arithmetic failures with complete rollback. Events report actual pool
balances. Buy's checked state updates and strict post-CPI risk limits are retained.
All 7,099 earlier comparisons pass on the same artifact. Twenty-six panic cases
retain diagnostic differences, including eight zero-effective-reserve unwrap
messages; errors, complete watched state, events and CPIs agree. Only
`initialize_mayhem_state` remains absent. Historical source and executable identity
remain unresolved.

```sh
python3 scripts/mayhem_pump_swap_differential.py \
  --candidate repro/mayhem/twentyfour/mayhem_recovered.so \
  --cases repro/mayhem/twentyfour/buy-pump-swap-cases.json \
  --instruction buy_pump_swap --family native --output work/mayhem-swap-buy.json
python3 scripts/verify_mayhem_pump_swap.py \
  --candidate repro/mayhem/twentyfour/mayhem_recovered.so \
  --receipts work/mayhem-swap-buy.json --output work/mayhem-swap-buy-verification.json
```

Use `sell_pump_swap` with `sell-pump-swap-cases.json` for sell, and `--family token`
or `--family token22` for the other configurations. All stored business states are
explicit simulator fixtures; no historical prestate or live authority is claimed.
Inherited legacy buy cases remain at `repro/mayhem/twenty/buy-cases.json`;
sell-v2 cases at `repro/mayhem/twentyone/sell-v2-cases.json`; and buy-v2 cases at
`repro/mayhem/twentytwo/buy-v2-cases.json`.
