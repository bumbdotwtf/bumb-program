# Mayhem: recovered administration paths

The current [Mayhem24 checkpoint](../../repro/mayhem/twentyfour/README.md) contains
24 recovered paths and 9,595 comparison receipts. Only the identified
`initialize_mayhem_state` handler remains absent; that initializer lane remains
stopped. Whole-original-byte equality and the security audit remain incomplete.

The opening observations below describe the earlier twenty-handler checkpoint
with 3,841 cases. Later sections record subsequent recoveries in order; their
counts and missing-path statements are historical, not the current inventory.

## Observed controls and behavior

The ten shared-context existing-state admin instructions require a signing, writable administrator;
GlobalParams must have the correct program owner, discriminator, valid Borsh
layout, writable flag, `global-params` PDA and matching stored admin. The System
program ID is validated. These paths also require the event-authority PDA and a
fifth program account. Even when no event is emitted, missing event/program
accounts reject. In the ten existing-state paths, account data shorter than 254
bytes fails deserialization; invalid paused booleans also fail.

The nine existing-state paths other than `update_global_params` do not validate
the fifth program key in the tested fixtures. `update_global_params` performs a
self-CPI and fails/rolls back when that provided account cannot support the CPI.
This difference is reproduced, not called a vulnerability: the first nine paths
perform no CPI through that unchecked account.

`initialize_global_params` takes three accounts, creates the 254-byte PDA via
the System program, and installs the signing payer as admin with other fields
zero. A synthetic uninitialized PDA may be initialized by the signer. This is not
a claim about the live PDA's present state, upgrade access, or exploitability.

Resetting SOL or stable deployment zeroes its respective 16-byte counter.
`reset_state` clears the observed risk/accounting ranges and unpauses trading
while preserving administrator, trader, version and the retained limit fields.
`stop_trading` requires active state; `resume_trading` requires paused state.
Both invalid transitions return 6000 (`TradingPaused`), including resume when
already active. This unusual error name is observed original behavior.

`update_global_params` accepts sixteen Borsh options in the recovered order. It
increments a u32 version even when all options are None. At u32::MAX it returns
6002 (`MathOverflow`) and rolls back all field updates. The event contains old
and new versions followed by the sixteen resulting values, totaling 129 bytes
including its discriminator. The original emits this both as log data and a
self-CPI; both are reproduced and compared.

## Dependency observations

Covered paths exercise the System program, Mayhem self-event entrypoint, and
captured token/ATA dependencies. Legacy buy and sell exercise the captured Pump CPI;
the remaining trade paths' dependency behavior is still unresolved.
The original Mayhem ELF contains full 32-byte constants for Pump at 0xae2ac,
PumpSwap at 0xae2e2, SPL Token at 0xad168/0xae302, and Token2022 at 0xae322.
This locates references for remaining CPI recovery; it is not proof of each
call's constraints or dependency build identity. A full-byte constant scan did
not find the captured Metaplex, donation relay or ATA IDs, but absence from that
scan does not prove absence of use. No unobserved Metaplex/relay CPI is assumed.

## Remaining work at the twenty-handler checkpoint

Five then-identified paths remained unimplemented: Mayhem state
initialization and four other Pump/PumpSwap buy/sell paths. Their
account/CPI constraints, price impact, risk accounting, rate limits, arithmetic,
rollback and dependency equivalence remain to be recovered and audited.
Historical source/build fidelity, executable layout and all bytes remain
unresolved. Current tests do not establish safety of those paths or the program
as a whole. No confirmed vulnerability is claimed by this partial work.

## Fee-recipient initialization and captured dependencies

The twelfth recovered path, `initialize_fee_recipient`, is covered by 306 further
strict differential cases, loading the exact captured Token, Token2022 and ATA
ELFs rather than relying on LiteSVM's builtin token programs. Valid indices 0–7
create a 42-byte program-owned FeeRecipient PDA and its native-WSOL ATA. Indices
8–255 return 6017 after the initialization CPIs and roll everything back. The
PDA seeds are `fee-recipient` plus the one-byte index. Its first two serialized
fields are bump and index; the remaining 32 bytes initialize to zero.

This initialization path requires a signing writable payer, but does not require
the payer to match GlobalParams.admin. GlobalParams must still be the correct
writable program-owned PDA. The native WSOL mint and legacy SPL Token addresses
are constrained; a valid Token2022 mint/program pair can reach initialization
CPIs but subsequently fails the token-program address constraint and rolls back.
These controls and ordering are reproduced. Permissionless creation of a fixed
program-owned fee-recipient PDA is not by itself a confirmed vulnerability.

The successful original calls establish actual ATA and token dependency use.
The earlier full-byte constant scan's missing ATA key was only a scan limitation.
Dependency source/build identity remains unproven even though captured binaries
are used for these local calls. Metaplex and donation-relay use remains unproven.

## Account extension and SOL withdrawal

`extend_account` accepts program-owned accounts with the recovered GlobalParams,
FeeRecipient or MayhemState discriminators, extending them to 318, 74 or 170
bytes respectively. It does not require a PDA or stored administrator. The signer
pays any rent shortfall, appended bytes are zeroed, and a log plus self-CPI event
records account, payer, old/new lengths and timestamp. Already large accounts
return without funding or events. Unknown types fail with 6016. The 301 cases
cover these boundaries and failed CPI rollback; permissionless rent-funded
extension alone does not demonstrate unauthorized fund extraction.

`withdraw_admin` requires the signing writable stored administrator, correct
GlobalParams PDA and `sol-vault` PDA, and transfers from the vault to that
administrator through the System program. The recovered rate check reads signed
i64 timestamp and interval at serialized offsets 138 and 154. When both are
nonzero, current time must be at least their sum; signed overflow panics as in
the original. A successful call writes current time even for zero amount. Failed
transfer and rate-limit calls roll back. Its 274 cases include extreme synthetic
configuration values; these do not prove an unprivileged party can create such
states or deny service on the deployed program.

The initialized FeeRecipient's trailing 32 bytes are zero, not the initializer's
public key. Preliminary original-only sweep probes further show stored trader
authorization for `sweep_fees` and stored administrator authorization for
`sweep_fees_admin`, with the authorized signer's wallet/ATA as destination.
Unauthorized signer fixtures fail the has-one constraint. These observations
reduce the initial creation-race concern but are not a complete sweep audit;
the additional recovered sweep checks and tests are described below.

## Quote withdrawal and sweeps

`withdraw_quote_admin` validates the stored administrator and vault PDA, creates
the administrator's quote ATA if needed, and transfers from the vault quote ATA
with the vault PDA as authority. It has a separate signed-i64 rate clock at
offset 238 and interval at 230, with the same zero-value bypass, checked-add
overflow and rollback behavior as SOL withdrawal. The context accepts token
interfaces, but its transfer instruction targets legacy SPL Token. A fixture
providing only Token2022 therefore fails with MissingAccount and rolls back,
rather than successfully moving Token2022 assets. The 329 cases reproduce this
original behavior with captured dependencies.

Both sweep paths require exactly sixteen remaining accounts, interpreted as
eight FeeRecipient/token-account pairs. The signer must match GlobalParams.trader
for `sweep_fees`, or GlobalParams.admin for `sweep_fees_admin`. Destination is the
signer and its already initialized quote ATA. The token-program address is
constrained to legacy SPL Token. A trader sweep applies the respective native or
stable aggregate limit; the administrator sweep is uncapped. Native sweeps move
wrapped tokens and excess recipient lamports, retaining rent for the actual
recipient account size. Non-native sweeps transfer tokens. Rent subtraction and
accounting overflow reproduce original panics on extreme synthetic state.

The FeeRecipient's trailing 32 bytes hold accounting fields: native timestamp
at 10, native cumulative amount at 18, stable cumulative amount at 26, stable
timestamp at 34. Trader sweeps update the appropriate timestamp even when moving
zero; admin sweeps preserve timestamps. Recipients are decoded and serialized
sequentially, so duplicate pairs observe earlier changes within the call.
Program ownership and account discriminators are checked. The recipient bump
and index authorize token CPI; native-only lamport movement does not require
those bytes to derive the provided account address. Token execution constrains
token authority and mint. These details match 692 differential cases, including
300 randomized fixtures and hostile token/recipient mutations.

The initially suspected permissionless recipient-creation concern has no
demonstrated fund-diversion path in these recovered instructions: initialization
stores no caller beneficiary, and sweep/withdraw destinations require the stored
trader or administrator. This is a bounded negative finding, not a declaration
that the entire deployed program is secure. The five absent handlers, live
configuration reachability and complete dependency source fidelity remain open.

## Genuine burn sequences

The recovered burn handler was tested with three unmodified finalized account
families, captured Clock and exact dependency executables. It burns the complete
vault balance, reduces mint supply, stores the amount, emits log/self-CPI events
and marks state ended. A second normally signed transaction in the same local
bank rejects with 6004 and changes only payer fees. All business state remains
untouched by fixture edits. The six instruction comparisons use twelve signed
transactions. Raw compute logs and source-location strings differ; the semantic
receipt lists precisely what was compared. These are current snapshots, not
historical replay or proof of all context/mode combinations.

The framework moved to the Anchor 1.0 family following static parser/CPI evidence.
An explicit source wrapper preserves original System-address checking, correcting
25 errors in an earlier draft. All inherited 2,953 cases pass after this change.
See [the complete evidence package](../../repro/mayhem/eighteen/README.md).

## Legacy sell

The recovered `sell` requires the writable signing trader named by GlobalParams,
the expected GlobalParams/state/vault PDAs, typed mint/token owners and ATA
relations, and the fixed Token-2022 and Mayhem program IDs. It retains the original
Mayhem-derived `bonding-curve-v2` PDA. Its distinct external curve decoder pads
short data to 141 zero-filled bytes and validates five boolean fields; burn's
strict curve decoder remains unchanged. Truncated data is still constrained by
subsequent arithmetic and the real Pump CPI, and is not treated as an authorization
bypass.

The 396 ordinary-signature synthetic cases compare complete watched account
state, balance/owner/rent metadata, errors, return data, events and inner CPI.
The original and candidate process the same signed transaction. All 134 successes
match the quote, 16-account Pump CPI, checked signed-128-bit accounting and 303-byte
event; all 262 rejections roll back watched business state. Rate/deadline ordering,
inclusive tolerance boundaries, caps, malformed accounts, every curve prefix
through 141 bytes, program substitutions, arithmetic extremes and post-CPI
overflow are covered. The simulator's stored trader is a genuine test-owned
keypair. No privileged initializer, foreign signature or authorization weakening
is used. This does not establish reachability of extreme synthetic states on the
deployed program or full historical sell replay.

All inherited cases and genuine burn sequences pass against the same combined
19-handler artifact. Compute usage and source-location diagnostics differ; the
zero-SOL panic also has an additional candidate Option-unwrapping message while
the runtime error and full rollback match. No confirmed vulnerability is claimed.
See [the nineteen-handler evidence package](../../repro/mayhem/nineteen/README.md).


## Legacy buy

The recovered `buy` preserves configured-trader authorization and typed accounts,
with 23 outer accounts and an actual 18-account Pump buy CPI. It uses the same
pause/rate/deadline/reserve-threshold and tolerance checks as legacy sell. Its
budget derives from current vault tokens and curve reserves, constrained by the
configured cap and retained real SOL. Token output is capped by real token
reserves; Pump receives that output and the full budget as maximum SOL cost.

After CPI/reloads, actual spent SOL increases the global and state signed-i128
counters, and acquired tokens reduce the state's signed-i128 token counter.
Checked overflow fails with 6002. Overall and per-coin limits are serialized
GlobalParams offsets 32 and 40; positive counters must be strictly below their
limits. Rejections are 6006 (`OverallRiskExceeded`) and 6007 (`CoinRiskExceeded`).
The original compares each positive counter's low u64 limb; the same truncation
is reproduced for synthetic values beyond u64::MAX. Those cases do not establish
reachable live configuration or an exploitable accounting condition.

The 486 cases include 187 successes and 299 rejections, using normally signed
owned-trader fixtures. They cover strict risk boundaries, negative/zero/large
counters, real-token caps, funding depletion and zero-lamport account removal,
volume windows, malformed accounts, flags and CPI failures. All watched account
bytes and metadata, errors, return data, events and inner calls agree. Independent
receipt checks verify signatures, exact quote/CPI inputs, full state/event bytes
and complete rollback after rejection. Post-CPI risk rejection rolls back Pump
changes as well as Mayhem state.

All inherited 3,355 comparisons pass on the same twenty-handler bytes. The actual
main-source build is wholly byte-identical to the reviewed isolated artifact;
neither matches the original executable. No initializer workaround or altered
authorization was used. Four raw panic-log differences remain documented, and no
full historical buy replay is claimed. See the
[twenty-handler package](../../repro/mayhem/twenty/README.md).


## Quote-aware sell

The recovered `sell_v2` requires the writable configured trader signer and the
original typed accounts, PDA/ATA relations, program IDs and account order. Its
31-account outer parser feeds an actual 26-account Pump sell CPI, signed by
Mayhem's own sol-vault PDA. Native quotes use GlobalParams cap/threshold/counter
positions 16/129/113; token quotes use 182/222/206. Actual SOL lamports or quote
vault tokens received drive checked i128 global/state updates. The state's quote
counter remains at 56 and token counter at 72. Complete 303-byte events zero
native-specific fields for token quotes while preserving the generic quote tail.

There are 473 synthetic cases each for native SOL, legacy SPL Token quotes and
Token-2022 quotes. Their 418 successful calls and 1,001 rejections match complete
watched account bytes/metadata/balances, errors, return data, events and inner
CPI. Independent checks reconstruct each successful quote and CPI payload,
complete state/event bytes, signed transaction validity and failed rollback.
Malformed accounts, every curve prefix through 141 bytes, guard ordering,
tolerance/cap boundaries, signed counters, flags and actual CPI failures are
covered. Invalid executable-account fixture mutations rejected during simulator
setup were excluded and retained separately, not counted as program rejections.

All 3,841 inherited comparisons pass on the same combined 21-handler artifact;
the clean main build is wholly byte-identical to the tested scratch artifact.
The three new families were rerun from their final repository paths. Four panic
log differences per family remain explicit; compute usage and source diagnostics
are not equivalent. Test-owned trader signatures and synthetic stored authority
are used with real PDA CPI signing. No initializer workaround, foreign signature,
authorization weakening, historical replay or live configuration reachability is
claimed. No confirmed vulnerability is established by these tests. See the
[twenty-one-handler package](../../repro/mayhem/twentyone/README.md).


## Quote-aware buy

The recovered `buy_v2` preserves the 32-account parser and actual 27-account Pump
CPI, using the configured ordinary trader signer and Mayhem's own sol-vault PDA.
Original-only and differential evidence establish read-only global-volume account
acceptance. The first draft's unnecessary mut constraint was removed after all
three matrices isolated it; the failed draft and receipts remain archived. No
trader authorization, typed ownership, PDA or ATA constraint was removed.

Quote arithmetic derives a capped budget and caps desired tokens by real token
reserves. Actual quote spent increases global/state signed-i128 counters and
acquired tokens decrease the state's token counter. Native overall/per-coin risk
limits are at GlobalParams offsets 32/40; token-quote limits are 190/198. Signed
positivity precedes the strict comparison of the counter's low u64 limb. Large
synthetic-counter cases reproduce this original behavior without establishing
live reachability or exploitation. Failed post-CPI checks roll back all watched
Pump and Mayhem accounts. Complete 303-byte log/self-CPI events agree.

There are 613 normally signed synthetic cases per native/legacy-token/Token-2022
quote family, totaling 704 successes and 1,135 rejections. All 5,260 earlier
comparisons pass on the combined 22-handler artifact. Independent checks verify
signatures, exact quote/CPI expectations, complete state/events, strict successful
risk limits and failed rollback. The clean integrated build is wholly identical
to the tested scratch artifact, with full original executable equality unresolved.
Four panic diagnostic differences per family remain. No historical prestate,
foreign signature, initializer workaround or confirmed vulnerability is claimed.
See the [twenty-two-handler package](../../repro/mayhem/twentytwo/README.md).


## PumpSwap buy and sell

The 31-account buy and 29-account sell parsers preserve the configured trader,
Mayhem PDAs, ATA relations, typed external AMM/token accounts and program IDs.
The quote-program interface is additionally constrained to Tokenkeg, while the
base program is Token-2022. Mayhem's Pool decoder zero-pads every short prefix to
287 bytes; its strict GlobalConfig decoder reads the older 418-byte prefix.
The Mayhem-derived pool-v2 account is validated but omitted from the actual CPI.
The CPI uses 25 buy or 23 sell accounts, and the only fixed signer is the actual
sol-vault PDA. Both buy volume accounts are writable, while the protocol recipient
is read-only inside the CPI. Remaining buyback flags are forwarded from AccountInfo.

The budget uses actual pool quote tokens plus signed virtual reserves, native or
stable caps, retained-reserve bounds and the recovered price band. Native buy
funds WSOL and synchronizes it; both native paths close WSOL back to the sol vault.
Actual accounting includes returned rent. Small native buys can therefore reach
the original checked-subtraction failure in these synthetic starting states;
complete watched state rolls back. This is behavioral evidence, not a claim of
live reachability or a confirmed vulnerability. Stable trades retain token
balance accounting and zero native-only event fields. Post-CPI risk checks on buy
retain the original strict low-u64 comparison after signed positivity checks.

The new matrix has 2,496 comparisons, including 680 successes and 1,816 rejections.
Six independent verifiers check all 4,992 signatures, successful quote sizing,
exact CPI payload/account order, full state and 303-byte events, and failed rollback.
All 7,099 inherited comparisons pass on the combined 24-handler candidate. The
clean main build matches the tested scratch executable. Twenty-six panic cases
retain source-diagnostic differences; eight also differ in unwrap-message detail.
No original executable, authorization check or signature was patched. No blocked
initializer experiment, historical replay or live chain mutation was performed.
See the [twenty-four-handler package](../../repro/mayhem/twentyfour/README.md).


## Field roles in the accepted Mayhem24 source

The [field-role crosswalk](../../repro/mayhem/field-role-crosswalk/README.md) binds the fourteen accepted compiler inputs and maps nine of sixteen neutral GlobalParams arguments to reads in the six recovered trade bodies. It separately records the nine MayhemState fields. Account byte offsets, candidate operations and unresolved historical names/types are kept distinct. Seven argument roles remain unresolved by this bounded review. The crosswalk adds no implementation, runtime receipts or security finding and does not inspect the stopped initializer.
