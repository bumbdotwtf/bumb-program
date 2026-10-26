# Pool serialization error conversion

The captured Pool account-exit function routes discriminator and field writer
errors through Anchor's `From<io::Error>`. The previous recovered serializer
constructed `ProgramError::BorshIoError(e.to_string())` at both source sites.
That expanded error formatting inside the generated exit and made its body
2,544 bytes, versus the original's 1,704 bytes. The correction changes only
`Pool::try_serialize` in `programs/pump-amm/src/state.rs`:

```rust
writer.write_all(Self::DISCRIMINATOR)?;
self.serialize(writer)?;
Ok(())
```

All 18 Cargo/source inputs were frozen against the preceding published AMM37
checkpoint before this one-function edit. The retained static evidence identifies
the exact write failure branches, raw displacements, original error conversion
call, direct helper bodies, discriminator bytes and the relevant cached Anchor
and Solana error-conversion source. All 90 sealed files and their original
manifest are preserved without resealing in the new package's
`static-evidence.tar.gz`. That report predates the build and correctly labels
its then-uncompiled patch as a hypothesis.

One isolated v1.44 clean build produced a 1,175,720-byte candidate, SHA-256
`5a68db39372121c6406727bced3087aa9caf63f14a999ac68206c9b5b3401216`.
All existing 25 suites were freshly run against those bytes: 17,462 comparisons,
zero mismatches, no new unique inputs. The same single source edit was then
promoted and clean-built from main paths with the same recipe. The entire main
executable equals the tested scratch executable, so those exact receipts apply
to the main-path build. Both build attempts succeeded; all suite attempts passed.

The new Pool exit at candidate `0x3c38` matches the complete original window
`0x4210..0x48b8` (1,704 bytes), after masking only actual relocation and direct-call
immediates in memory. All 24 direct target bodies match at their original
targets; consumed Pool discriminator bytes also match. The prior GlobalConfig
exit match remains: original `0x4f00..0x5570`, 1,648 bytes and 24 matching direct
targets. The candidate has 448 of 641 normalized function matches, versus 447
before this correction. Candidate function sizes come from the independently
built symbol ELF; original bounds are inferred entry/call boundaries.

These results do not establish full transitive data identity or historical source,
compiler, dependency or flag identity. The independent raw whole-file and
ELF-extent comparisons both remain unequal to the original. No output binary,
header, relocation, symbol or section was modified to produce any match.
The implementation remains 37 of 38 handlers. `create_config` remains unrecovered
in active source; this work adds no initializer or runtime probes.

The immutable package is
[`repro/pump_amm/pool-serialization-thirty-seven`](../../repro/pump_amm/pool-serialization-thirty-seven/README.md).
It includes main/scratch build records, exact source and helper snapshots,
runtime bindings, all fresh receipts, the historical static evidence archive,
the portable verifier and the previous checkpoint reference. Verify with:

```sh
python3 repro/pump_amm/pool-serialization-thirty-seven/verify.py
```

The portable verifier rechecks package manifests, all source/test archive hashes,
original static raw windows, whole-file main/scratch identity, complete normalized
exit/direct-target/discriminator matches and all 25 saved receipts. A repository
path additionally checks 18 current source inputs and 13 runtime inputs. All
36 helpers/harness inputs are verified in the archive; scratch-only paths absent
from a clean checkout are reported separately instead of requiring local work
directories. The previous serializer package remains unchanged.
