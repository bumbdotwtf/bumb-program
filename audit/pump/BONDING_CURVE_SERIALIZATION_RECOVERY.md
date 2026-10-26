# BondingCurve serializer source recovery

This checkpoint changes only `programs/pump/src/trade_types.rs` from the published
Pump48/five-partial source. It preserves all handler and partial-path counts. The
known `sell_v2` quote-transfer-fee minimum-output/event mismatch remains, and the
candidate is not a deployable replacement.

The original `BondingCurve` exit occupies `0x5a28..0x6158` (1,840 bytes). The prior
candidate's corresponding 1,976-byte body wrapped serialization failures as
Anchor error 3004. The original instead propagates the ordinary I/O error. The
source now writes the discriminator and calls Borsh serialization with `?` for
both operations. The Anchor account macro owned the previous serializer, so it
is replaced by equivalent explicit discriminator, owner, serialization and
deserialization traits, while retaining the same Clone/Borsh derives, field order
and layout. Deserialization logic remains the same; macro source coordinates may
move with the explicit implementation.

The effective lock uses `anchor-lang` 0.31.1 and `anchor-attribute-account` 0.31.2.
An initial reference read used the cached account-macro 0.31.1 file; its complete
bytes were then confirmed identical to the effective locked 0.31.2 file. The
source reference and this distinction are retained in the package. There is no
claim that these locks uniquely identify the historical dependency graph.

One clean isolated v1.44 build produced a 1,534,768-byte candidate with SHA-256
`92575cd082bf76b332044a7d09371a9764db8b2cc40180bf1418f261945bbd6a`.
Its complete exit body at `0x7110` is 1,840 bytes and matches the original after
normalizing only actual ELF relocation and direct internal-call immediates.
All 25 direct-call sites lead to matching complete target bodies, covering six
unique targets. The one consumed eight-byte discriminator is exactly
`17b7f83760d8ac60`. Raw body bytes differ because of addresses; transitive rodata
and historical source identity are not established. No executable bytes,
headers, relocations, padding or compiler flags were altered.

Only after the static match passed were all 37 existing differential suites
(9,217 comparisons) and 28 unchanged Surfpool runners (1,024 comparisons) replayed.
All passed. Saved differential receipts contain 15,830 transactions and 24,216
verified signatures. Surfpool receipts contain 2,048 signed transactions and
2,980 verified signatures. The partial native curve suite keeps its existing 56
cases: 50 reach Pump through the captured AMM's genuine PDA-signed CPI, six stop
in AMM and only 11 succeed. No fixture, trade-fee experiment or stopped recovery
lane was added.

The [frozen package](../../repro/pump/bonding-curve-serializer-fortyeight/README.md)
retains the complete sealed scratch handoff, a separate clean main build, both
source maps and snapshots, build/compiler/dependency records, all signed runtime
receipts and a whole-file main/scratch identity report. The main build uses the
same fixed v1.44 recipe with unchanged locks/profile and 36 actual inputs.
Complete executable identity is required before reusing the scratch runtime
receipts; main promotion does not add runtime cases.

Each receipt has a binding to the scratch executable and its actual compiler
inputs, plus an identity-backed main-source binding. Legacy embedded source maps
are preserved as baseline checkout snapshots and are not represented as the
compiled serializer inputs. Quote-control directly binds its adjacent scratch
build report. The unchanged runner/helper closure and public captured runtime
binaries are hash-bound. Post-build dependency archive/source observations do
not prove that caches were immutable throughout compilation.

A preparation preflight stopped before any runtime test because the unused
aggregate validator changed independently. Its diagnostic and old/current hashes
remain preserved; the aggregate was never invoked by these runners. The isolated
build itself had no failed attempt. Generated deployment keypairs are neither
read nor packaged.

Full original executable equality, exhaustive serialization/error behavior,
historical compiler/dependency/source identity and the security audit remain
incomplete. The matched serializer body improves source fidelity without closing
the existing behavior-coverage gaps.
