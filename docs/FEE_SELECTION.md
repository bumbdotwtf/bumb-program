# Pump Fees: first recovered implementation fragment

`programs/pump-fees/recovered/fee_selection.rs` recovers the selector at original
SBF addresses `0xab158..0xab2d0`. The get_fees wrapper is at `0x9b500`, located
through its official discriminator comparison and direct wrapper call. No machine
code is embedded in the Rust source or substituted into its compiler output.

Platform-tools **v1.43**, rustc **1.79.0-dev**, LLVM **18.1.7**, produces a 376-byte
function. All instruction bytes match except seven bytes within the unresolved
panic-location and panic-function relocation fields. The first 356 bytes are
identical. The unlinked object is preserved unchanged, not patched to manufacture
a function match. The two relocations and all differences are recorded in
`repro/experiments/fee-selector-v143.json`.

Platform-tools v1.52 produces 448 bytes and differs starting at byte 2. Both
compiler versions, compiler executable hashes, source hashes, commands and object
hashes are retained. This identifies a compatible code-generation candidate for
one function; it does not uniquely identify the historical compiler, establish
whole-program identity, or resolve the panic metadata and dependency graph.

## Behavioral evidence

The native compilation of this same Rust selector matches **1,215** successful
calls to the captured original `get_fees` instruction in LiteSVM. Fixtures include
sorted, unsorted and duplicate thresholds; exact and adjacent thresholds; u128
limits; absent/false/true quote flags; and varying u64 trade sizes. The selected
schedule is normal tiers for an absent/false flag and stable tiers for true.
Non-Pump pools return flat fees. These conclusions cover the tested get_fees
interface, not the distinct get_fees_with_quote_mint interface.

Selection first returns the first tier if market cap is below its threshold,
then scans backwards for the last qualifying tier. Empty selected tiers panic at
`pump-fees-math/src/lib.rs:49:23`. An invalid quote bool produces Anchor error 102.
The fixture's complete serialized fields fit well below the allocation required
by the original deserializer: 2,511 bytes fails, 2,512 succeeds. This is a measured
boundary for this fixture, not a fully recovered deserializer specification.

The complete cases and negative probes are recorded in
`repro/experiments/fee-selector-differential.json`. All accounts are synthetic and
execution is local. Unsorted or empty schedules are intentionally injected to
recover semantics; reachability through real configuration updates is unproven.

## Reproduce

Install `requirements.txt`, then use a fresh output directory:

```sh
python3 scripts/build_fee_selection.py --toolchain /path/to/platform-tools-v1.43 \
  --output work/fee-selector-build
rustc --edition 2021 -O programs/pump-fees/recovered/fee_selection_host.rs \
  -o work/fee-selector-host
python3 scripts/validate_fee_selection.py --host work/fee-selector-host \
  --output work/fee-selector-validation.json
```

Native rustc reports an unused no_std attribute when importing the selector as a
module; the SBF compilation uses it as a crate root. Native test output is separate
from the SBF object comparison. No complete program has yet been rebuilt.

`evidence/dispatch-map.json` also maps all 125 official IDL discriminators across
Pump, PumpSwap and Pump Fees, plus 25 Mayhem discriminator hypotheses derived from
instruction log names and confirmed as comparison constants in the binary. The
map locates wrapper entrypoints for subsequent recovery; it is not recovered
handler source or a claim of complete dispatch coverage.

## Quote-mint routing recovery

`quote_fees.rs` now recovers the routing behavior at `0x3f748..0x3f9d8`,
called by the original `get_fees_with_quote_mint` wrapper at `0x9bb18`.
Non-Pump pools return flat fees. For Pump pools, the default (zero) key, wrapped
SOL, and `9pan9bMn5HatX4EJdBwg9VgCa7Uz5HL8N1m5D3NdXejP` select the normal
schedule; USDC selects the stable schedule. Other quotes select exotic fees,
falling back to flat fees only if all three exotic fee fields are zero. The
third normal-quote constant's identity is not inferred from its address.

The native recovered routing matches **9,428** original SBF queries, including
empty schedules/panics, unsorted schedules, boundary market caps through u128 max,
non-Pump pools, partial-zero exotic fees, and mutations of every byte of the four
recognized quote constants. The deterministic complete case report is gzip-compressed
at `repro/experiments/quote-selector-differential.json.gz`. Native Rust and original
SBF behavior agree within these cases; the reconstructed account layout is an
observed internal layout, not a recovery of the complete account parser.

The original calls a comparison shim at `0xc2730`; its relocation names the
`sol_memcmp_` syscall. `memory_compare.rs` recovers that shim's semantics and
uses a native byte loop for the host harness. An opaque Rust-ABI declaration
keeps the recovered router's comparisons out of line. This is an explicit
reconstruction boundary, not evidence of the original source's declaration or
symbol name. Ordinary Rust slice comparison instead compiled into inline loads.
The selected SBF builds preserve both unlinked objects without patching.

Platform-tools v1.43 produces a **656-byte** router, equal in length to the
original but **not equal in instructions**. v1.52 produces **648 bytes** and also
differs. Their manifests are `repro/experiments/quote-selector-v143.json` and
`quote-selector-v152.json`; objects are in the corresponding experimental binary
directories. Neither compiler has been established as the historical compiler.
The recovered comparison shim also differs from the original's 64-byte function.
Linking, relocations, full handler validation, and whole-program identity remain
unresolved. These objects are not deployable replacements.

```sh
python3 scripts/build_quote_host.py --output work/quote-host
python3 scripts/validate_quote_fees.py --host work/quote-host/quote-fees-host \
  --output work/quote-validation.json
python3 scripts/build_quote_fees.py --toolchain /path/to/platform-tools-v1.43 \
  --output work/quote-sbf
```

Synthetic empty/unsorted configurations are deliberate semantic probes;
reachability through the actual administration instructions remains unproven.
No vulnerability is established by those injected states.

## Independently executing query handlers

`programs/pump-fees/` now builds an experimental complete SBF executable with two
implemented query handlers, four implemented admin handlers, and 25 unsupported handler bodies. This advances beyond
native math comparisons: 10,789 cases compare execution of that compiled candidate
with the original in separate LiteSVM instances. They check returned fees, error
codes, unchanged account data and unchanged account lamports. They cover both
query interfaces, missing/truncated arguments, PDA/owner/discriminator/allocation
checks, malformed vector lengths, and the earlier threshold/quote matrices.
No mismatch was observed. Log text, compute cost, and full instruction coverage
are not established. Original-versus-candidate byte comparison remains unequal.

The first Anchor 0.30.1 build differed on all inputs shorter than eight bytes.
Anchor 0.31.1 resolved those differences without a custom dispatcher patch.
Further parser probes distinguished InvalidAccountData (bad discriminator or
short allocation) from BorshIoError (malformed vectors). The selected lockfile
is reproducible but remains a candidate, not the recovered historical graph.


## FeeProgramGlobal administration

The same independently built executable now also implements `set_authority`,
`set_social_claim_authority`, `set_disable_flags`, and `set_claim_rate_limit`.
444 additional differential cases compare errors, account bytes/owner/lamports,
payer balance changes, event payloads and signed self-CPI instructions. These
include every u8 flag value, u64 boundaries, malformed arguments, and account
validation failures. Together the six handlers have11,233 passing SBF cases.
The captured original rejects a zero main authority with6001, permits a zero
social-claim authority, and rejects unauthorized signers with6016. No security
conclusion is extended to the25 unimplemented handlers. The current source,
compiled ELF, build log and complete receipts are pinned under
`repro/pump_fees/admin-six/`. All whole-program comparisons remain unequal.
