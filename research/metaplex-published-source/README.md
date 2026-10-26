# Metaplex published crate source: bounded negative provenance result

The published crates inspected here do not identify the recovered Metaplex source.
This extends the [existing Git-history study](../../repro/pump/metaplex-authentic-source-history/REPORT.md)
with independently distributed registry archives, including source before the
November 2022 processor refactor. It finds 108 additional distinct source snapshots
at the 18 recovered file paths, but no exact recovered file, added patch block,
or target diagnostic-anchor placement in this bounded comparison.

## Registry evidence and results

The [crates.io response](https://crates.io/api/v1/crates/mpl-token-metadata) saved on
2026-10-26 enumerates the selected versions: all 55 `1.x` releases/prereleases,
plus `2.0.0-beta.1` and `2.0.0`. All 57 compressed archives (6,638,100 bytes total)
were downloaded from the registry's version endpoints, followed to
`static.crates.io`, and matched their registry SHA-256 checksums. Exact archives,
the registry response and per-request receipts are included. No archive content
was extracted to the filesystem or executed.

| Observation | Result |
| --- | ---: |
| Selected archives verified | 57 |
| Versions containing the on-chain Utilize handler | 56 |
| Legacy monolithic `src/processor.rs` handler versions | 26 |
| Split `src/processor/uses/utilize.rs` handler versions | 30 |
| Distinct full files containing those handlers | 25 |
| Handlers retaining the exact total/remaining two-disjunct guard | 56 |
| Handlers containing a literal `number_of_uses == 0` or reversed equality | 0 |
| Distinct source snapshots at the 18 recovered paths | 151 |
| Those snapshots absent from the earlier Git-history packet | 108 |
| Exact or whitespace-insensitive complete recovered-file matches | 0 |
| Complete added patch blocks found as consecutive normalized lines | 0 |
| Accepted diagnostic anchor at its saved original line | 0 |

The legacy full-file count is not a count of distinct Utilize function bodies:
other functions in `processor.rs` also changed. Each archived handler contains
the exact two-disjunct guard after whitespace normalization:

```rust
if number_of_uses > metadata_uses.total || number_of_uses > metadata_uses.remaining {
```

The split handler places `metadata.uses.unwrap()` on line 70 or 73. The earlier
monolithic versions place it at recorded lines between 965 and 1289. None supplies
the target's saved Utilize line 85. The 29 diagnostic observations reuse the
hash-pinned candidate-11 classification; this work does not re-decode the target.
The complete 33-block comparison reuses the pinned recovered-hunk ledger, with
missing historical file paths represented as missing rather than matches.

The package boundary is material: `2.0.0-beta.1` still contains the on-chain
processor, whereas `2.0.0` contains the generated Rust client and declares
`clients/rust` in its VCS metadata. Treating every 2.x version as client-only would
omit the beta's program source. Versions `1.2.0` through `1.2.6` contain no
`.cargo_vcs_info.json`; that absence is explicit. Other versions' embedded VCS
claims are retained, not asserted to be independently verified Git associations.

## Check of declared Git locations

A separate follow-up queried the exact repository from each archived
`Cargo.toml.orig`, the commit and package path from `.cargo_vcs_info.json`, and
the complete file containing Utilize. All 49 program releases that declare a
VCS revision participate. The GitHub connector returned source for 44 locations;
every returned file equals its published archive member byte-for-byte. These
are 19 legacy `processor.rs` observations and 25 split `utilize.rs` observations,
not 44 distinct source texts or whole-repository verifications.

The other five queries returned `No commit found for the ref` in the declared
`metaplex-foundation/metaplex-program-library` repository:
`1.13.1-beta.1`, `1.13.1`, `2.0.0-beta.1`, `1.13.2-beta.1`, and `1.13.2`.
Those responses remain unresolved observations, not evidence that the revisions
never existed or cannot be found elsewhere. The seven releases without VCS
metadata cannot supply such a query. The `2.0.0` client is outside this
program-handler comparison.

`vcs-observations.json.gz` preserves all 49 connector results, including complete
successful source text, exact queries and failed responses. A literal digest
seals the uncompressed observation bytes. `verify_vcs.py` first rechecks the
original registry/archive evidence, derives the queries from those archives,
then replays the complete-file comparisons and verifies `vcs-findings.json`.
It performs no network calls. Changed source, incorrect query bindings, missing
or duplicate rows, substituted failure types, rewritten findings and output
replacement are covered by nine tests, including a minimal relocated replay.

```sh
python3 -B research/metaplex-published-source/verify_vcs.py
python3 -B research/metaplex-published-source/test_verify_vcs.py
```

These are source-content observations at GitHub-served commit URLs. They do not
independently authenticate Git commit objects, verify the rest of an archive
against Git, or attribute a deployed build to those revisions. The original
findings and their `vcs_commit_association_independently_verified: false` fields
remain unchanged. No new handler source variant, target guard or byte-identity
improvement was found in this follow-up.

## Reproduce offline

Use Python 3.11 or newer, with the standard library, from the repository root:

```sh
python3 -B research/metaplex-published-source/analyze.py
python3 -B research/metaplex-published-source/test_analyze.py
```

The first command authenticates the saved registry response and acquisition
receipts against literal pins, verifies every archive against the registry
checksum, and checks the six external source-evidence inputs. It reads regular
archive members in memory, rejects duplicate/nonregular members and unsafe names,
then recomputes and compares every row of `findings.json.gz`. It requires no
network, compiler, target ELF, VM, Cargo cache or original author's scratch paths.
The archive inventory must exactly equal the selected registry versions.

To inspect the complete findings as ordinary JSON, choose a fresh output path:

```sh
python3 -B research/metaplex-published-source/analyze.py --output work/published-source-findings.json
```

The tests include replay from a minimal relocated repository, altered registry
and acquisition receipts, corrupt/missing archives, altered external evidence,
changed saved findings, output preservation and positive/negative source probes.
The first exploratory analysis rejected absent optional VCS metadata; the final
reader records it as `null` and all seven absent cases participate in replay.

## Limits

These checks concern exact source text in the specified registry snapshot, not
semantic equivalence or exhaustive historical-source recovery. The literal guard
and patch-block searches do not detect every equivalent spelling, macro expansion
or private change. Textual diagnostic anchors do not prove compiler source spans.
The top-level function-span locator is deliberately a text observation, not a Rust
parser. Complete source bytes remain available in their authenticated archives.

Registry checksums identify distributed bytes, not the uploader's build, the Git
revision used, or the provenance of the deployed program. The 18 recovered files
are comparison targets, not newly authenticated historical source. Later client
releases, other crate names, private forks and unpublished archives are outside
this search. No candidate was built or promoted; the existing byte gaps remain
unresolved.

## Third-party licensing

The files under `archives/` are unmodified third-party crate distributions,
redistributed byte-for-byte for offline verification. They are not covered by
this repository's own license; each archive remains under the license its
`Cargo.toml` declares, as recorded in `crate-metadata.json`:

| Versions | Declared license | License text inside the archive |
| --- | --- | --- |
| `1.1.0`, `1.2.0`-`1.2.5` (7) | `Apache-2.0` | none; SPDX identifier only |
| `1.2.6`-`1.5.0` (17) | `AGPL-3.0` | none; SPDX identifier only |
| `1.6.0`-`2.0.0` (33) | Metaplex NFT Open Source License (`license-file`) | `LICENSE` |

Authorship metadata is preserved in each archive's `Cargo.toml`.
