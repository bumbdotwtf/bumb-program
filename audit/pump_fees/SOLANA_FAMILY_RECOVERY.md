# Solana dependency-family recovery

The current Fees candidate combines the accepted social-v2 account layout with one provenance-backed dependency-family change. The candidate is 768,072 bytes, SHA-256 `e501ca2c744373e5653a5ac7e25a3fd20f6058765808b888c3605fd03adba60f`. It remains different from the 948,944-byte captured program: 419,662 differing positions in their shared length, with a −180,872-byte length difference. This is dependency recovery evidence, not unique historical source or compiler attribution.

The controlled graph replaces exactly eight of 253 selected packages; all other 245 selections remain unchanged. Every replacement appears together in the retained official `spl-tlv-account-resolution 0.10.0` release `Cargo.lock` (SHA-256 `7a9af8f255c523b98880013a783ebc4d3d92e0213c257739be6ae143570e4e58`). The official crate archive is bound by SHA-256 `1408e961215688715d5a1063cbdcf982de225c45f99c82b4f7d7e1dd22b998d7`. The Fees manifest and Anchor 0.31.1 selection remain unchanged.

| Package | Previous selection | Selected family |
| --- | --- | --- |
| solana-instruction | 2.3.3 | 2.2.1 |
| solana-loader-v3-interface | 5.0.0 | 3.0.0 |
| solana-program | 2.3.0 | 2.2.1 |
| solana-pubkey | 2.4.0 | 2.2.1 |
| solana-signature | 2.3.0 | 2.2.1 |
| solana-sysvar | 2.3.0 | 2.2.1 |
| solana-vote-interface | 2.2.6 | 2.2.1 |
| solana-zk-sdk | 2.3.13 | 2.2.0 |

Actual offline Cargo resolution, its locked repeat, and the combined build confirm those exact selections and their resolved feature sets. The preliminary conservative graph analysis counted 251 active nodes; Cargo also retains the already-selected `bytes` and `tinyvec` weak-feature metadata nodes, yielding 253. No unplanned version was added. All 252 registry archive checksums and extracted source contents were checked. The only new retrieval was the official `solana-zk-sdk 2.2.0` archive, whose checksum was bound before retrieval; its VCS record identifies `8b11c7d5bf529ed690f4954cb1f96c8be66bb8e8`, while the other seven changed archives identify `1c1d667f161666f12f5a43ebef8eda9470a8c6ee`.

The source change reproduces both captured Pubkey source records: `create_program_address` at `src/lib.rs:131:18` and `find_program_address` at `src/lib.rs:612:32`. Six complete symbol-sized Pubkey helpers match inferred original function windows after explicitly documented in-memory normalization of internal-call and loader-relocation immediates. The 1,520-byte base58 formatter, all ten direct call targets, and all seven formatter source records match; the 40-byte Display/Debug wrapper is raw-byte identical. This replaces the earlier 5,512-byte formatter mismatch. The proof is bounded to those full windows, direct calls and pointed records, without claiming all transitive data or a unique version fingerprint.

The accepted social-v2 layout is unchanged: boxed quote mint and by-value event-authority/program `AccountInfo` fields. Its complete original 560-byte generated exit, seven direct calls and three literals still match in the combined ELF. The static matcher records 409 of 519 candidate ranges as bounded and call-consistent; these are diagnostic function ranges, not handler counts or complete program equivalence.

The combined scratch candidate freshly passed all 17,441 existing comparisons and ten persistent donation-sequence steps using frozen copies of 46 harness files and 18 runtime inputs. The unchanged saved-evidence verifier checks all existing assertions and 17,204 signatures in 8,644 encoded transaction fields. The two genuine historical signed messages remain unchanged and are verified separately. Sixty-nine comparisons repeat existing inputs with stronger assertions; no new handlers or unique fixture cases are claimed. The finalized main source is clean-built separately, and receipts transfer only upon exact whole-file identity with the tested scratch ELF.

The unchanged build recipe requests platform-tools v1.44 compilation, while the retained SDK `env.sh`/installer selects platform-tools v1.52 before `strip.sh` invokes `llvm-objcopy`. The package records compilation and stripping separately, including SDK source hashes, observed links/markers and tool-file hashes. These observations do not retrospectively prove the process-level tool hash for every earlier historical invocation, nor establish the captured program's original tool pipeline. No compiler/flag matrix, source padding, executable patching or re-stripping variant was used.

The [publication package](../../repro/pump_fees/solana-family-221-v144/README.md) preserves the complete sealed pure graph trial and combined trial, including original graph provenance/seals, the earlier unsatisfied graph history references, the pre-build missing-helper failure, official archives, source/build/helper manifests, raw static evidence and all fresh receipts. The missing `analyze.py` import failed before Cargo/compiler launch and was restored verbatim from the frozen baseline Git revision. The earlier [social-layout checkpoint](../../repro/pump_fees/social-v2-account-layout-v144/README.md) remains historical evidence for its distinct `c181b0ba…` executable. No live chain action or new runtime fixture was introduced.
