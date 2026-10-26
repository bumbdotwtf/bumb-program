# Pump.fun byte-identical source checkpoint

Shaw's reconstructed [`dao_v1`](../../third_party/daosfun-source/docs/BUILD.md)
has a published clean source-build receipt and the same whole-file SHA-256 as
this lab's pinned deployed DAO ProgramData. The local
[artifact comparator](shaw-dao-baseline.json) confirms equality of the
published binaries; it does not recompile Shaw's source here. An exact binary
proves an equivalent build artifact, not unique original names or comments.

For Pump.fun, the [official public docs](../../third_party/pump-public-docs)
provide the current IDLs and client-facing behavior, not the deployed Rust
instruction bodies. The [official Pump.fun GitHub organization](https://github.com/pump-fun)’s public
repository listing was checked on 2026-10-24 and contained docs and SDK
projects, with no whole-program source identified for these three deployed
executables. That is a source-discovery observation, not proof no copy exists
elsewhere.

| Program | Declared selectors | ProgramData bytes | ELF bytes | `.text` bytes | Zero allocation padding | Whole SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| [Pump bonding curve](pump-fun-pump-baseline.json) | 56 | 10,485,715 | 1,934,800 | 1,792,208 | 8,550,915 | `7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d` |
| [PumpSwap](pump-fun-amm-baseline.json) | 38 | 10,485,715 | 1,268,504 | 1,162,040 | 9,217,211 | `6a7ad34596d83b4c435b32f458a56e718e9f82eb4ad38e4316616d15d24d8ff7` |
| [Pump Fees](pump-fun-fees-baseline.json) | 31 | 948,944 | 873,256 | 799,648 | 75,688 | `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e` |

These are read-only finalized ProgramData captures with byte-level ELF
section and padding records. All 125 published discriminators have mapped
dispatcher wrappers, but a selector map is not instruction-body source. The
three ELF headers use SBF machine value **263** and flags **0**; Shaw's DAO
capture uses `EM_BPF`. The tested local `cargo-build-sbf` v4.1.0 / platform-tools
v1.54 / Anchor 0.30.1 recipe emits the same Pump Fees machine/flags and
section names, but this is only a toolchain-format compatibility check.

The initial [Pump Fees candidate](../../reconstruction/pump-fun-fees-candidate/README.md)
is generated from the pinned 31-instruction IDL with ordered accounts,
signer/writable flags and argument types. It compiles twice from clean target
directories to the same [candidate hash](../../reconstruction/pump-fun-fees-candidate/build-reproducibility.json).
All 31 selectors reach intentionally unsupported handlers under constructed
local accounts in [LiteSVM](../../reconstruction/pump-fun-fees-candidate/interface-verification.json).
The candidate ELF is **289,528 bytes** with **244,256 `.text` bytes**, versus
873,256 and 799,648 for the deployed Fees ELF. The [section and byte
comparison](pump-fun-fees-candidate-compare.json) reports no whole-ELF match.
The candidate is an interface scaffold and must not be deployed.
The [machine-checked source-match ledger](pump-fun-source-match-status.json)
tracks all three deployed hashes and refuses to count this scaffold as a
complete or byte-identical rebuild.

Next source work is to reconstruct Pump Fees account constraints, fee math,
state transitions, token/system CPIs and error order against the pinned ELF,
replacing each unsupported handler only after local differential evidence.
Then pin the actual compiler/dependency graph and linker ordering, compare
section/relocation spans, and require an exact ELF SHA plus the deployed
ProgramData zero padding. Pump and PumpSwap require their own complete source
and the same final binary check. **0/3 Pump.fun programs are byte-identical
source rebuilds today.**
