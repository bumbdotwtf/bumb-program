# bumb-program

Source reconstruction of the pump bonding-curve programs, maintained as the reference for [bumb](https://bumb.wtf), a 1:1 pump-style launchpad on Solana. The recovered program sources live under `programs/` (`pump`, `pump-amm`, `pump-fees`, `mayhem`, `donation-relay`); `docs/`, `audit/`, `research/` and `evidence/` hold the reconstruction notes and captured on-chain evidence.

This repository is a trimmed snapshot of the reconstruction research originally published at lalalune/pumpfun-source. The 16 GB `repro/` evidence packages referenced throughout `docs/` are not included here; links into `repro/` resolve only against that upstream archive.

---


Captured deployment evidence and source reconstruction for Pump.fun Solana programs. **Byte-identical reconstruction remains incomplete.** Captures retain complete account payloads, hashes, observation slots and loader metadata. See [scope](docs/SCOPE.md).

Current selected artifacts must agree with [status.json](repro/status.json) and the complete pass-26 byte/function index. Whole-file identity remains **0/4 core programs**. Dependency capture images remain **2/5**; only SPL Token is a whole-file exact raw compiler output (**1/5**). Token-2022 and Metaplex allocation images are recorded separately from shorter raw compiler output. No overall reconstruction percentage follows from finite tests or normalized function matches.

| Program | Selected executable SHA256 prefix | Differing or missing captured positions |
| --- | --- | ---: |
| Pump | `71ec4d8a646eefc8` | 9,784,703 |
| PumpSwap | `09bee0dfd751dc6a` | 9,958,512 |
| Fees | `2387f8139a13918a` | 554,122 |
| Mayhem | `ca5d4f54b14e2f67` | 501,010 |
| Donation Relay | `5f6d29410047551f` | 614,726 |
| ATA | `ba8dd8a42ca7bff4` | 307 |
| Metaplex retained image | `2c26e081f3faabf0` | 1,509 |

Positional counts include common-extent differences and missing allocation bytes; they are not semantic distance or a completion score. The 3,338 original windows remain fully represented: Pump 1,035, AMM 785, Fees 585, Mayhem 441 and Relay 492. Opaque, unmatched, ambiguous, call-conflicting and stopped rows remain explicit.

The selected Pump remaining-guards checkpoint restores evidenced owned errors and rejection predicates. Mayhem uses the measured official v1.54 recipe with unchanged source. AMM restores plain collect-owner error 6048 without compared Pubkeys. Fees retains the sharing-authorization checkpoint. Relay retains source 15's owned arithmetic errors. Clean managed-source builds reproduce the tested Pump, AMM and Mayhem executables and symbols. Relay's selected canonical source is bound, but a fresh build from that canonical path is not claimed.

Existing corpora contain 9,269 Pump, 17,462 AMM, 17,461 Fees and 9,595 Mayhem comparisons. Pump also has 1,024 signed Surfpool comparisons; Fees has ten separate sequence steps. Counts overlap and include repeated inputs. They support bounded reconstruction of 140/150 identified instruction dispositions, with five partial and five unrecovered handlers. They do not establish exhaustive behavior, security acceptance or exact captured bytes.

The Pump virtual-params reconstruction remains an unaccepted proposal. Its first successful compile exposed an AccountInfo ownership mismatch during emitted review; no current handler or coverage count is added. Broader creation/trading/routing, parser/error/cleanup, recursive call/data, historical source/compiler/dependency and SDK acceptance obligations remain open. ATA's 307 differences and Metaplex's 1,509 retained-image differences lack an evidence-backed further build correction.

Stopped executions remain excluded: the new Pump sell_v2 corrective/transfer-fee probe; Pump admin-update/claim token incentives; Mayhem initializer; old V3 token-extension leaf; additional Metaplex runtime; and filtered BuyV3 partial-fill. No new signer, PDA, owner, source-origin or history bypass, fabricated source coordinate, binary patch/padding, or flag/layout sweep is part of the current checkpoint.

```sh
python3 scripts/verify_evidence.py
python3 scripts/test_tooling.py
```

Use [completion and remaining work](docs/COMPLETION.md), [build-identity evidence](docs/BUILD_IDENTITY_AUDIT.md), [parallel ownership](docs/PARALLEL_WORK.md), and the latest complete layered-pass ledgers for detailed boundaries. [Pass 25](repro/layered-passes/pass-25/README.md) is the published predecessor; historical packages remain immutable. [Current status](repro/status.json) and [Relay current selection](repro/donation-relay/current.json) identify the accepted artifacts.

Original bytes remain under `evidence/`. Raw compiler output is distinguished from retained allocation images; no padding or byte editing converts an unequal compiler output into a match. Imported harnesses submit signed tests only to offline loopback simulators. No on-chain deployment is claimed. Upstream materials retain their authorship; this repository does not assert a license over them.

The [integrated research lab](research/README.md) retains import provenance and replay tools. The security audit and live SDK/deployment acceptance remain incomplete. Historical checkpoint descriptions are preserved in Git and in the per-pass evidence packages; their candidate pointers are not current selections.
