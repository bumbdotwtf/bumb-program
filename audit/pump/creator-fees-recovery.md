# Pump creator-fee recovery review

The current creator-thirtythree checkpoint implements 33 recovered handlers and
four partial paths: buy_v3, sell_v3, buy_exact_quote_in_v3 and create_v2. All 6,338
differential cases across 28 suites and 694 Surfpool comparisons (1,388 signed
transactions across 21 runners) passed. Full-file byte identity remains false.
The original capture is 10,485,715 bytes, SHA256
`7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d`.
The clean v1.44 candidate is 1,129,592 bytes, SHA256
`85358197282b1c5579dbccc623d407bab2e04e0fae1c72e1b6066a5f8bc25292`.
[The frozen package](../../repro/pump/creator-thirtythree/README.md) binds 25 source
inputs, 68 harness files and 205 manifest entries. All 1,388 transaction signatures
were independently verified. Earlier checkpoint counts remain historical evidence.

This checkpoint adds legacy sell, sell_v2 and legacy migration, and extends partial
creation to whitelisted quote/control-consumer paths. It corrects stored creator-fee
overrides, exact-input fee overflow order and completion reserve accounting in the
reconstruction. These are reconstruction differences, not original-program
vulnerability findings. Mayhem/nested creation and untested v3 quote routes remain
incomplete. Compiler and dependency identity remain unresolved.

## Recovered behavior

Collection transfers native vault lamports above the empty-account rent floor.
An executable recipient or zero available amount returns without a payout event.
PDA seeds bind the vault to the recipient; System Program enforces its transfer
ownership/data rules. The reconstruction does not replace that authorization.

Distribution binds mint, curve, foreign-owned sharing state and creator vault.
A stored creator mismatch or paused sharing configuration rejects distribution.
Ordered remaining recipients must match the shareholders, be non-executable and
have nonzero shares. Native distribution computes the maximum recipient rent
deficit scaled by its share. Below this threshold it returns a zero-distribution
structure without transferring or emitting the event. At and above the threshold,
payouts use floor division, retaining rounding residue. Duplicate recipients,
nonstandard aggregate share totals, sharing versions and the revoked flag are
accepted in the tested stored-state variants; these synthetic states are not
proof that every such state is reachable through original creation/update paths.

The minimum-fee query shares recipient validation and rent arithmetic but permits
paused sharing state. It emits a log event and returns the minimum, available fees
and eligibility result without modifying accounts. Legacy curve fields preserve
the original defaults and invalid-Boolean decoding errors.

V2 token distribution parses the source token account before recipient validation,
checks the quote, and uses grouped wallet/ATA remaining accounts. Missing recipient
ATAs either reject or are created through the actual associated-token program.
SPL Token and Token2022 enforce transfer ownership, mint and frozen-account rules.
Normal test-owned transaction signatures and genuine program CPI signing are used.

## Evidence and limits

The maintained differential suites compare full relevant account snapshots,
errors, event bytes, return data and recorded inner instructions. Surfpool performs
signed offline transactions and compares state/errors and events with only the
known timestamp normalized; raw payloads and signatures remain in its receipts.
Source-to-capture identity, exhaustive state-space equivalence, every token extension
combination and unrecovered handlers remain unproven. No new vulnerability claim
is inferred solely from permissive synthetic state or dependency errors.

All 1,924 differential cases and 50 Surfpool comparisons (100 signed transactions)
passed on the integrated candidate. Frozen artifacts and exact counts are recorded under `repro/pump/creator-eighteen/`.
The build records compiler identity, source hashes, lockfile and command. Original
ELF bytes are read only after compilation for comparison and are not compiler inputs.


## Expanded creator and lifecycle checkpoint

The creator-twentyfive source adds token collection, extension, volume sync,
creator/protocol sweeps, creator migration and administrative creator changes.
Each focused implementation was independently compiled and compared before
combined regression. The integration candidate remains byte-different.

Additional destination-substitution coverage found that the original rejects an
existing same-mint ATA belonging to a different wallet with6054; the earlier
reconstruction omitted that address check. The new implementation preserves the
original rejection. The test creates the alternative ATA through the captured
ATA program with an ordinary signature, without editing its token authority.
Earlier bounded passing fixtures did not cover this substitution. Treat this as
a corrected reconstruction gap, not a vulnerability in the captured original.

The migration path requires matching sharing administration, rejects holder
creator changes, and requires accrued creator fees to be swept. It allows protocol
fees to remain. Short legacy curve layouts preserve original post-event write
failures and transaction rollback. Administrative CTO includes actual captured
Fees/AMM CPIs, token/native payouts, frozen-wallet behavior, holder conversion,
fee configuration constraints and curve rent/size handling. These observations
remain bounded by saved synthetic fixtures and normal signature verification.


The combined creator-twentyfive candidate is 690,480 bytes with SHA-256
`a1edac573ea08b5456116ca8bea53ed570d4e5dcae21c72cc438103d75774213`.
All 3,741 differential cases across 16 suites and 176 Surfpool comparisons
(352 signed transactions) passed. The eight destination-substitution cases now
reject consistently in the original and candidate. Surfpool replays initialized
poststates; the genuine signed ATA-creation bootstrap transactions and initialized
account snapshots are retained separately, rather than claiming the bootstrap was
rerun by Surfpool. Exact source/build/receipt manifests are in
`repro/pump/creator-twentyfive/`. These results supersede the earlier candidate for
this expanded scope, without establishing full binary equality.


## Parameter, creator-setter and IDL authority checkpoint

Creator-twentynine adds `set_params`, `set_creator`, `set_metaplex_creator` and
`admin_set_idl_authority`. The new suites add 169, 509 and 171 cases respectively,
with the two creator setters sharing one suite. Parameter updates preserve reserve
arithmetic, validation precedence, sorted recipient checks and unrelated Global
fields. Creator setters retain observed metadata decoding, creator restrictions
and legacy curve serialization. These bounded fixtures do not establish every
possible metadata or account-state combination.

IDL authority uses actual Anchor account deserialization and serialization after
its observed resize/discriminator checks. The original differs between runtimes
on six short-header fixtures: lengths 0/7 return InvalidRealloc in LiteSVM and
6010 in Surfpool; lengths 8/31/40/43 return InvalidRealloc in LiteSVM and succeed
in Surfpool. The final candidate matches the original within each runtime. The
receipts retain these cross-runtime differences explicitly; they are not hidden
by normalizing errors or skipping comparisons.

The current package supersedes creator-twentyfive for this expanded scope. It
preserves raw signed transactions, logs and fixtures. Recognized event timestamps
are normalized for comparison while raw values remain available. Some Surfpool
return values are retained without comparison; each deterministic suite records
its own comparison scope. Alternative ATA bootstrap transactions remain separate
from the 484 Surfpool transactions. These results do not establish production
safety, exhaustive behavioral equivalence or historical compiler/dependency
identity. No new original-program vulnerability is inferred from this checkpoint.


## Creation and exact-quote integration

The creator-thirty candidate adds one recovered handler, legacy create, and
two partial handlers: normal SOL create_v2 and buy_exact_quote_in_v3. It therefore
contains30 recovered handlers plus four partial paths. The clean candidate is
955,072 bytes with SHA-256
`273e07ca4d27788bbf8eedd8a901b521ebce7406400610f4edce5f1198940ab2`.
All 5,139 differential cases across 22 suites and 346 Surfpool comparisons
using 692 signed transactions pass. Source/harness hashes remain unchanged, and
the package manifest verifies all 156 files. Full byte equality remains false.

Legacy create initializes the mint, curve and ATA, invokes captured immutable
Metaplex metadata creation, mints supply and revokes authority. Metadata string
limits are enforced by the actual dependency. The create_v2 partial branch uses
Token-2022 metadata initialization, holder creator substitution and byte-length
checks; it explicitly rejects unrecovered Mayhem and quote remaining-account
branches using a reconstruction-only error. Those rejections are not attributed
to the original.

Exact-quote recovery exposed and corrected candidate mismatches through expanding
fixtures: tiny spend/error ordering, migration-fee underflow, funded completion,
quote-dependent post-completion reserves, Mayhem partial-fill slippage behavior
and one-unit fee rounding. Protocol and creator fee ceilings use the original
unadjusted net quote, while the recorded quote may be decremented for affordability.
Ordinary completion can continue into a post-completion pool; oversized Mayhem
partial fills stop at completion. Full state, CPI arrays, events and return values
are compared in deterministic fixtures. These are reconstruction corrections, not
a new security assessment of the original protocol.
