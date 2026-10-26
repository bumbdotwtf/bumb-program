# Donation handler recovery draft

This isolated partial Anchor crate recovers `create_donation_fee_pda` and `crank_donation_fee_pda` from the captured Pump Fees executable. It is a hand-written behavioral reconstruction, not the original source, a complete Fees implementation, or a byte-identical build. Other handlers are absent. Integration into the shared Fees crate belongs to the main reconstruction task.

The fixture scripts use normally signed transactions, test-owned payer keys, synthetic account state and the captured dependency executables in an offline LiteSVM instance. They compare transaction errors, account data/ownership/lamports, events and inner instructions. Compute-unit consumption and source-location log text are not acceptance criteria. These tests supplement the signed Surfpool transaction suite documented in `../../README.md`; they are not themselves Surfpool RPC tests.

## Observed behavior

Creation checks disable bit 4, validates the mint and curve, and initializes a canonical donation PDA. Existing nonzero versions return without replacing state. New or version-zero state validates the AMM pool using its stored bump and checks its coin creator. A sharing-config creator additionally requires the active, non-revoked sharing administrator. Initialization resets counters and reserved bytes.

Cranking checks disable bit 8, initializes the donation token account if necessary, wraps excess native SOL, and invokes the captured Donate.gg relay with a message containing the base mint and creator. The credited-to identifier is the Fees program. Successful nonzero forwarding increments the donation total and timestamp and emits an event. A zero balance returns after account initialization. The token account remains open after forwarding. Tested timestamps did not enforce a cooldown. These are observed behaviors, not conclusions about exploitability.

The relay source and IDL attribution are documented in `../../relay/README.md`. The source repository advertised by the relay is unavailable publicly; its captured executable is used as a dependency for these tests, not presented as a source rebuild.

## Reproduce

From repository root, with the environment from `localnet/setup.py` installed:

```sh
work/localnet/venv/bin/python scripts/build_partial_candidate.py \
  --manifest localnet/recovery/fees-donation/crate/Cargo.toml \
  --program pump_fees --artifact-name pump_fees_candidate.so \
  --output work/donation-draft-build
work/localnet/venv/bin/python scripts/fees_donation_create_differential.py \
  --candidate work/donation-draft-build/artifacts/pump_fees_candidate.so \
  --output work/donation-create.json
work/localnet/venv/bin/python scripts/fees_donation_crank_probe.py \
  --candidate work/donation-draft-build/artifacts/pump_fees_candidate.so \
  --output work/donation-crank.json
```

The build helper uses a fresh target directory and isolated SDK/rustup aliases and records the selected compiler, source hashes and honest full-file mismatch. The selected Anchor 0.31.1 / platform-tools v1.52 environment is a candidate environment, not proof of the original compiler or dependency versions. The output directory must not already exist.

## Frozen validation

The candidate SHA-256 is `8f1ac2f1fd9d1a25953f9a08bc8e88d5c5b951331675c96e92c2a9ff34912b44`. All 356 creation and 357 crank fixtures match the captured original for their compared fields. The compressed receipts retain every case and transaction. Build provenance refers to the scratch source paths; `source-manifest.json` maps the copied source paths to their hashes. The candidate is 329,120 bytes; the original is 948,944 bytes and full-byte equality is **false**.

A separate Surfpool 1.6.1 run passed all 10 original/candidate comparisons (20 normally signed transactions: seven successes and three expected rejections per executable). Account data, ownership, lamports and errors match, excluding only the wall-clock `last_crank_ts` field; raw timestamps and logs remain in `surfpool-transactions.json.gz`. Reproduce with:

```sh
work/localnet/venv/bin/python localnet/donation_transactions.py \
  --candidate localnet/recovery/fees-donation/pump_fees_candidate.so \
  --output work/donation-surfpool
```

A persistent creation/deposit/crank sequence also matches across 10 steps (20 signed transactions). It preserves donation and relay state through repeated normal System transfers and same-time, one-second-later and one-day-later cranks, then an empty crank. Account changes, errors, events, return data and inner instructions are compared; the Fees executable bytes and their size-dependent initial rent are excluded while program lamport deltas are compared. Receipt: `sequence.json.gz`.

```sh
work/localnet/venv/bin/python scripts/fees_donation_sequence.py \
  --output work/donation-sequence.json
```
