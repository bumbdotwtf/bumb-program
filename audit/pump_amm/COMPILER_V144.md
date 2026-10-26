# PumpSwap v1.44 checkpoint

The main AMM crate now uses the validated v1.44-compatible Cargo.lock. Its twelve
Rust source files and Cargo.toml are unchanged from the 32-handler cashback
checkpoint. A fresh main-path build produced 889,472 bytes with SHA-256
`f2d54e4529f94ad49a3e2fd5afe4e497df62e407d62d9f0d819788f43f583823`.

The complete main output equals the scratch v1.44 output. Consequently, the
scratch executable's 21 suites and 14,635 passing original/candidate comparisons
apply to this exact executable. The package preserves their original commands
and receipts and explicitly records the identity-based reuse. They are not
represented as a second set of transactions executed on the main build.

The captured original remains different: 10,485,715 bytes, SHA-256
`6a7ad34596d83b4c435b32f458a56e718e9f82eb4ad38e4316616d15d24d8ff7`.
The first difference is byte 24, with 492,903 differences in the shared length.
Equality through the parsed ELF extent is also false. Both files have machine 263
and flags 0. Header compatibility does not identify the historical compiler.

The compiler and dependency graph changed together. Existing compatible pins
were selected to address actual resolution/MSRV constraints: blake3 1.8.2,
proc-macro-crate 3.3.0, indexmap 2.11.4, unicode-segmentation 1.12.0, zeroize 1.8.2,
and zeroize_derive 1.4.2. These pins are reproducible candidate inputs, not proven
historical dependency versions. No arbitrary graph search or binary editing was
used. The preserved prior v1.52 cashback package remains a separate checkpoint.

The build used locked/offline Cargo, an isolated cache with 254 checksum-verified
archives, and fresh target/SDK/rustup directories. Source and lock hashes, compiler
and SBF standard-library hashes, exact commands, cache/index hashes, both failed
metadata attempts and their source snapshots are retained. A root-owned build
helper improvement landed after this build launched; the exact executed helper
and both updated helper modules are separately frozen and labeled. The standalone
crate's input manifest remains 14 files under both helper versions.

Reproduction and provenance are in
[`repro/pump_amm/compiler-v144`](../../repro/pump_amm/compiler-v144/README.md), including
`main-scratch-identity.json`, `build-helper-provenance.json`, and
`manifest-sha256.json`. All synthetic-state, signature, CPI, error-normalization
and coverage limits of the existing suites remain in force. This is a compiler
compatibility checkpoint, not an additional source-recovery or security-audit
claim. Six published IDL handlers and complete original-program equivalence
remain unresolved; the independent scan frozen at 329fc44 excludes this work.
