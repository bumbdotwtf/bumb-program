# Fresh v1.37 compiler observation

**A newly authenticated platform-tools v1.37 installation successfully initializes
the expected rustc-driver in the pinned image.** This crosses the cold-image
installation boundary established by the parent package. It does not establish
which libraries were loaded in the historical candidate-11 build.

[Successful run 40333550925](https://github.com/startrack3r/pumpfun-source/actions/runs/40333550925)
executed revision `91bec1a763af9ddbbd6175ceb339f7ccf79d7eb5` on Ubuntu 24.04.
The exact 95-member artifact ZIP is retained here, with GitHub run, job and artifact
metadata in `receipts.json.gz`. Its SHA256 is
`5997bf576992f188487280cd2d8f4a701a8302a6fc4592127a37768ad82d0cbb`, matching the
provider artifact digest. The retained observer and executed workflow match their
exact Git revision blobs. The workflow is a fork-only controller; it is not a
change to the upstream workflow inventory.

## Observed compiler and capabilities

The runner downloaded the official 362,756,282-byte archive and checked SHA256
`8d5153589dbe19635affe937663cf4555a7e69a62d91ab4a1df064aaa8d5f066` before installation.
This independently rechecks the bytes identified by
[PR #50](https://github.com/lalalune/pumpfun-source/pull/50); the publisher provides
no archive digest. All 2,426 archive headers are retained, together with hashes of
the entrypoint, driver and `version.md`. Compiler binaries are not committed.

The image digest is the parent package's
`43206149a565ec35da95b1a909f4714f5d5f0d8241c31df24189e517acd18467`;
Docker inspection confirms configuration ID
`8a1c7e411dda3083f89fc82e9fbcbc57cfffed615853f11c124ef3df1443978f`.
The archive was unpacked into a new tmpfs cache with the container network disabled,
a read-only root filesystem, dropped capabilities and no program source or captured
executable mounted. The pre-install missing-path command observes that empty tmpfs;
the parent package's layer analysis establishes the clean image's cache absence.
This experiment explicitly installs the archive; it does not execute or trace the
SDK's automatic installer.

All 44 recorded commands succeeded, including cleanup. During `rustc --version
--verbose`, `LD_DEBUG=libs` reports nine library initializer paths. Their resolved
files were hashed in the same container. In particular, the initialized driver is
`rust/lib/librustc_driver-f767167903553d17.so`, SHA256
`e7d221509c0d5f5430175547b6d972e300892258bfa6e1b0cf1c4058a73ad9f2`, equal to the
197,537,432-byte archive member. The trace and `ldd` output are retained separately:
search attempts are not treated as initialized libraries. This is a file-identity
observation, not an exhaustive process-memory or loader-interpreter attestation.

The compiler reports Rust `1.68.0-dev`, unknown commit/date, and LLVM `15.0.7`.
The archive's `version.md` names Rust commit
`764ce69bd00903f5c59f44b6aa72649b173f568c`; this is archive metadata, not a newly
discovered embedded compiler commit or a source rebuild.

| Rust target | LLVM target | Explicit features in target specification |
| --- | --- | --- |
| `bpfeb-unknown-none` | `bpfeb` | none recorded |
| `bpfel-unknown-none` | `bpfel` | none recorded |
| `bpfel-unknown-unknown` | `bpfel` | `+solana` |
| `sbf-solana-solana` | `sbf` | `+solana` |

For all four targets, the compiler lists CPUs `generic`, `probe`, `sbfv2`, `v1`,
`v2`, `v3`. The raw feature queries distinguish rustc features (`alu32`, `crt-static`)
from LLVM code-generation features (`dummy`, `dwarfris`, `dynamic-frames`,
`reloc-abs64`, `sdiv`, `solana`, `static-syscalls`). These are available capabilities;
the JSON specifications do not contain an explicit `cpu` field, and these queries
do not identify the CPU/features used by the historical compilation.

## Reproduce and inspect

The saved replay needs only Python 3.11+ and its standard library. It authenticates
both exact ZIPs and provider snapshots, verifies every command log's bytes and hash,
rederives the loaded-driver binding and capability summary, and prints the results.
It does not extract or execute compiler programs and works outside the repository.

```sh
python3 -B research/metaplex-image-bootstrap/installed/verify_saved.py
python3 -B research/metaplex-image-bootstrap/installed/test_observe.py
python3 -B research/metaplex-image-bootstrap/installed/test_saved.py
```

The ZIPs contain the original individual logs, archive inventory, observation JSON,
observer source, workflow and source revision for inspection with any ZIP reader.
Thirteen tests cover archive/loader checks, isolated replay, changed evidence,
driver substitution despite unchanged version output, network-setting changes,
failed queries and unsupported historical-attribution promotion.

For a fresh observation, use an isolated Linux x86_64 runner with Docker, curl and
Python, sufficient memory for the 2 GiB tmpfs limit, and a new output directory:

```sh
python3 -B research/metaplex-image-bootstrap/installed/observe.py --output /tmp/metaplex-installed-new
```

Acquisition uses network access on the runner. The compiler container uses
`--network none`. The large archive stays in the output's `downloads/` directory;
the compact `evidence/` directory contains success or failure logs. Fresh runs will
have different timestamps/container IDs and are not substitutes for the sealed
historical observations retained here.

## Retained failure and remaining boundary

[Run 40332914951](https://github.com/startrack3r/pumpfun-source/actions/runs/40332914951)
failed with a connection reset while following the archive download redirect,
before any Docker command or compiler execution. Its four-member artifact is
preserved unchanged: SHA256
`d173a8e3837838491b1dcf3c6049c92016da63fb972dff411ce9ec996554db14`.
The successful revision uses curl with bounded retries and retained transfer
diagnostics. No failed output was replaced by an expected result.

The next diagnostic gate remains a reproduction of candidate 11's **raw**
707,448-byte output, SHA256
`3bbaf27ff0c10ff68d8a195a82f39eadee266f324067bd0a66081710be30b4ec`, before interpreting
IR or machine-IR traces as belonging to that candidate. This increment compiles no
program, replays no target, promotes no artifact and improves no raw target-byte
match. The padded allocation image remains a separate object.
