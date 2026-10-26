# Byte-identity audit: provenance and backend-diagnostic follow-ups

This supplement follows the [published audit](BUILD_IDENTITY_AUDIT.md) at `a73a4f2e`. The core checkpoint source, accepted artifacts, status and prior evidence packages remain unchanged. Full original-byte identity remains 0/4 core programs and 2/5 dependency payloads.

## A zero Cargo exit does not establish backend or runtime readiness

The initial [v1.47 frozen Fees-graph experiment](../repro/identity-audit/2026-10-25/relay-v147/REPORT.md) has one backend `Error:` diagnostic: a `driftsort_main` stack offset 4104 exceeds 4096 by 8 bytes, with estimated frame 4160. Cargo and strip nevertheless returned zero. Its exact formatter/Unicode/multiply positives remain valid byte evidence; that experiment never established an accepted program or runtime result. This supplement makes the backend limitation explicit without rewriting the original sealed packet.

A subsequent [single v1.47 build of the actual frozen Relay source build 12](../repro/donation-relay/source-build-12-v147-measurement/REPORT.md) preserves all 23 source/lock inputs and the original release profile. Cargo and fixed strip return zero; the 501,144-byte output has SHA-256 `a6244e332aa2dcfdad3c27852e8c9542ac2c94b33371a71802d538cadf52face`. It remains different from the captured Relay. Complete entry-bounded/call-consistent library matches are 106/120 selected emitted bodies, versus 33/98 for the retained v1.44 build of the same source; bounded raw-exact counts are 25 and 5. These counts are diagnostics, not source-completion percentages or a uniform historical compiler proof.

The actual Relay build emits **two** such backend stack diagnostics. Its linked code contains a direct `r10` access at -4112; the packet records full entry/body bounds and instruction bytes. No runtime was executed, and this does not establish that every input reaches that access or that every program invocation fails. The artifact is retained strictly as compiler/source evidence. No source/profile/feature repair, retry, accepted-artifact promotion or SDK acceptance follows.

The saved Mayhem v1.53/v1.54 logs and the clean supported adapter v1.54 build log contain no anchored backend `Error:` lines. Absence of a reported diagnostic is still not a complete stack-safety, VM-verifier or behavioral proof. Direct research Cargo builds intentionally remain separate from the historical driver's additional validation stages.

The new [diagnostic gate](../scripts/check_sbf_backend_diagnostics.py) reads plain or gzip build logs without modifying them. It returns 1 when an anchored backend `Error:` is present, while retaining the actual compiler/strip exits in their original receipts. This is a separate readiness check, not an automatic change to the historical or research build drivers. Five compiler-free regression cases cover zero-exit footers, compressed/ANSI logs, multiple errors, false command-line matches and the distinction between no reported errors and readiness.

```sh
python3 -B scripts/test_sbf_backend_diagnostics.py
python3 -B scripts/check_sbf_backend_diagnostics.py \
  --log repro/identity-audit/2026-10-25/relay-v147/build-02/build.log.gz \
  --log repro/donation-relay/source-build-12-v147-measurement/build-01/build.log.gz
# Expected diagnostic-gate exit: 1. The historical compiler/strip exit codes stay 0.
```

## ATA source lock and official asset identity are authenticated

The [ATA provenance packet](../repro/ata/authentic-build-provenance/REPORT.md) independently authenticates the complete official f5ce86 source lock and its Git blob/tree relationship. Its lock hash is exactly candidate2's `3c8f402f40488908503e9cc088388c1f95848d79da5141b5cb1a14006d74428b`. Both current official v1.1.0 release assets also match the captured 105,032-byte ATA hash `6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d`; neither asset metadata record supplies a publisher digest.

What remains unproved is the association of that asset with the source checkout/lock actually used, host/BPF Cargo and compiler closure, feature/unit graph and full compiler invocations. The same-tree PR head was committed after both asset uploads; it is not a newly discovered preupload committed source. Empty present-day status/check/review/artifact responses provide no build association and do not prove CI never ran. The API's default `pending` state with zero status contexts is not evidence of a pending build. No new source/flag/compiler experiment is justified by these bounded negative records.

The exact 307-position residual remains unchanged. No Docker daemon, executable bytes, chain accounts or stopped research lanes were changed.
