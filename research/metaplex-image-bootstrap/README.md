# Metaplex image bootstrap and fresh compiler provenance

**Candidate 11's recorded SBF compiler is not preinstalled at its cache path in
the clean pinned image.** The SDK installs platform-tools later. The historical
build script measures the compiler after `cargo build-sbf` completes, so those
post-build observations cannot be assumed to describe the untouched image.

The follow-up [fresh compiler observation](installed/README.md) authenticates and
installs official v1.37 bytes into an ephemeral cache, records the initialized
driver and nine library file hashes, and queries BPF/SBF capabilities successfully.
It retains both the initial transport failure and the successful hosted run.

This explains the missing-path boundary observed in community
[PR #50](https://github.com/lalalune/pumpfun-source/pull/50), without repeating
its failed container command or changing its evidence. It provides an independent
static check for the diagnostic reproduction proposed in
[PR #46](https://github.com/lalalune/pumpfun-source/pull/46). Neither PR is required
to replay this package against main.

## Evidence

The complete Docker registry manifest is bound by image digest
`43206149a565ec35da95b1a909f4714f5d5f0d8241c31df24189e517acd18467`.
Its configuration SHA256 is
`8a1c7e411dda3083f89fc82e9fbcbc57cfffed615853f11c124ef3df1443978f`,
equal to the historical image ID. All eight compressed layers were downloaded
(888,493,373 bytes), checked against the manifest, streamed without extraction,
and checked against the configuration's complete uncompressed diff IDs, including
tar padding after the end marker. This static layer check executes no container or
binary; the separate `installed/` experiment executes compiler queries.

All 28,844 tar headers are retained as losslessly compressed inventories. None
adds `root/.cache` or a descendant; both `root` records are directories. This is
a narrow absence check for that path in this image, not a general overlay or
symlink resolver, and it does not claim there are no other compiler programs.
The original large layer blobs remain outside Git; a full replay can download
and authenticate them again.

The Solana layer retains `version.yml` declaring SDK **1.16.25**, source commit
`8dd7d060a83a4310c14d9b931d4409fc1ad27117`. Its `sdk/sbf/scripts/install.sh`
is exactly equal to the file served at that immutable upstream revision
(SHA256 `428b42a324e89789e8d6ce732803032bb56f9165f79a5872217d896b8d7508ee`).
The corresponding pinned
[cargo-build-sbf source](https://github.com/solana-labs/solana/blob/8dd7d060a83a4310c14d9b931d4409fc1ad27117/sdk/cargo-build-sbf/src/main.rs)
sets default platform-tools `v1.37`, constructs the home cache path, downloads and
unpacks a missing package, and links the `solana` rustup toolchain before building.
The image's build-wrapper executables are hashed in `layers.json.gz`; no independent
rebuild of those wrappers is claimed. Upstream source retains its license.
The three generated JSON receipt files retain their original Windows line endings
inside lossless gzip containers; their literal seals cover the uncompressed bytes.

Four pinned candidate-11 records bind the image, compiler path, raw comparison and
build-script ordering. The compiler at
`/root/.cache/solana/v1.37/platform-tools/rust/bin/rustc` is measured only after the
build subprocess. This source ordering and the authenticated image contents
establish the installation boundary; they do not reconstruct every event in the
historical container.

## Reproduce

Python 3.11+ and the standard library suffice. The default replay checks the fixed
manifest/configuration, sealed inventories and selected source members, SDK source,
and four historical records. It is offline and does not execute the historical
build script, image programs or contract code.

```sh
python3 -B research/metaplex-image-bootstrap/verify.py
python3 -B research/metaplex-image-bootstrap/test_verify.py
```

For the stronger check, download the exact compressed blobs to a fresh directory,
then reproduce every header, selected-member hash and uncompressed layer digest:

```sh
python3 -B research/metaplex-image-bootstrap/fetch_layers.py --output work/metaplex-image-layers
python3 -B research/metaplex-image-bootstrap/verify.py --layers work/metaplex-image-layers
```

The downloader uses anonymous Docker registry pull authorization, retains failed
downloads and receipts, and refuses an existing output directory. It does not
extract or run an image. The local full-layer replay passed on Windows with Python
3.13.7. Fifteen tests cover relocated replay, changed receipts/source/inventories,
missing layers, root aliases and cache paths, compressed and uncompressed integrity,
tar padding, download hash failures and output preservation. The first synthetic
layer test used a path outside the selected SDK prefix; the fixture was corrected
without changing production selection or any observed image data.

## Limits and next diagnostic step

Saved inventory replay checks retained observations. Full-layer replay additionally
derives those observations from bytes authenticated by the pinned image digest.
Registry digests identify content; they do not attest who built the image.
Source inspection is not an executed trace of the binary build wrapper.

The `installed/` follow-up prepares and authenticates a fresh platform-tools
installation and observes its driver and initialized library files. These new
measurements do not recover historical loaded-library hashes. Candidate 11's exact
707,448-byte raw output must still be reproduced before
attributing IR or machine-IR traces to that candidate. No new candidate build,
target execution, selected-artifact change or byte-identity improvement is claimed
here; the retained allocation image remains distinct from raw compiler output.
