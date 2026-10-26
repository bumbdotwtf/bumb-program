# Social claim v2 context-layout recovery

This checkpoint preserves all 31 Fees instruction bodies and the same bounded
runtime corpus. It changes the in-memory `ClaimSocialFeePdaV2` account context,
not persistent account layouts: `quote_mint` becomes boxed, and `event_authority`
and `program` become by-value `AccountInfo` fields with their existing constraints.
The source remains an experimental reconstruction, not a deployable replacement.

The original complete exit at byte offsets 405560–406120 is 560 bytes. The first
fixed-v1.44 trial boxed only the quote mint. Its strict complete-body comparison
failed at offset 88: the candidate loaded `context+0xc0`, while the original
loaded `context+0x120`. Its source, clean successful compiler attempt, executable,
strict verifier failure and diagnostic remain preserved. It was not accepted and
did not run runtime comparisons.

Independent read-only parser analysis then identified the two event-CPI fields.
Original account-parser calls at 397848 and 398544 reach the same 416-byte account
consumer, with bounded error labels `event_authority` and `program`. The consumer
clones the 48-byte `AccountInfo` representation. Original successful parser output
holds those values at `0xb8..0xe8` and `0xe8..0x118`; the boxing-only candidate
holds eight-byte references instead. The original mint pointer is at `0x120`,
and the first candidate's is at `0xc0`. These dataflow observations support the
second source correction. They do not establish a general Rust field-order rule,
complete parser equivalence or a unique historical source spelling.

The selected locked Anchor event-CPI macro sources use `AccountInfo` for these
two fields. Initial 0.31.1 macro reference reads are retained separately from the
effective 0.31.2 source references. The preserved context-layout review explains
this distinction and binds the source contracts. No lock, profile, compiler flag,
padding or executable-byte variant was introduced.

The second clean trial produced 770,624 bytes with SHA-256
`c181b0ba75aee67369385e04908d89088552c1fad756bf5a21d7fb21979e6a58`.
Its 560-byte exit at 209184 matches the original after normalizing only actual
relocation and direct-call immediates. All seven direct-call sites reach matching
complete callee bodies (six unique targets). Three consumed literals, of 32, 14
and 10 bytes, match exactly. Raw exit and whole executable bytes remain different
from the captured original. The proof does not recursively establish every
callee's data references or complete source identity.

The clean main build has the same complete executable bytes as the accepted
second trial. Both bind 22 source/workspace/IDL/documentation inputs. The main and
second-trial source snapshots differ only in the bound program README; all Rust,
Cargo and IDL bytes are identical. The actual main build and runtime input maps
are retained without rewriting the scratch maps.

All runtime comparisons were freshly executed against this main candidate:
17,331 comparisons in the unchanged 18-suite aggregate and 110 comparisons in
eight focused reports, totaling 17,441 receipts. Sixty-nine repeat existing inputs
with stronger signed-transaction or error/log assertions. The separate persistent
donation sequence has ten steps. No new handler or unique fixture was added. The
two initializer successes use the exact genuine historical signed messages;
signature verification remains enabled, and only stale-blockhash freshness is
adapted for local replay. This is not a full historical-bank reproduction.

The [package](../../repro/pump_fees/social-v2-account-layout-v144/README.md) preserves
both trials, complete sealed static reviews, main build/source inputs, actual
helper/runtime snapshots, all fresh receipts and a portable verifier. The runtime
assertion body is copied unchanged from the immutable FeeConfig serialization
checkpoint, retaining historical-message identity, signature checks, compared
value logs, codec logs, donation steps and serialization rollback assertions.
The 46 executed helper/reference files and the separately captured orchestrator
are identified as distinct provenance groups. Generated deployment keypairs are
neither read nor packaged.

The bound program README retains an older opening checkpoint pointer alongside
its appended social-v2 section. This package records that documentation limitation
without changing the 22 inputs after their clean build. Earlier Surfpool receipts
remain evidence for their named prior executable and are not claimed as fresh
validation of this one.

Full original-byte equality, exhaustive behavior and account constraints,
historical compiler/dependency/source identity and the security audit remain
incomplete.
