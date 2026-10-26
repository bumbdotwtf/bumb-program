# Buyback handler recovery draft

This standalone partial crate reconstructs `initialize_buyback`, `update_buyback_authority`, `update_buyback_claim_rate_limit`, and `sweep_buyback` from normally signed execution of the captured Pump Fees executable. It is a behavioral draft for integration, not the historical source, a complete Fees implementation, or a byte-identical rebuild.

The fixtures use synthetic local state and test-owned signing keys. No real authority keys, signature bypasses or live transactions are used. The original captures are unchanged. The frozen source hashes were checked against the clean-build receipt; `source-manifest.json` maps the copied paths. `artifact-manifest.json` records hashes for the evidence package.

## Observed behavior

Vaults use `["buyback-vault", index]` seeds. Initialization accepts indexes 0–7, allocates 208 bytes and creates the vault ATA. It leaves all vault fields zero, including authority. Global authority can then assign the vault authority and claim rate. The setter accepts the tested signed 64-bit rate extremes; the sweep requires the configured vault authority's normal signature.

Sweep requires initialized source and destination ATAs even for a SOL-only transfer. It invokes `TransferChecked` before moving native lamports and updating checked counters. Native rent retention uses the vault's actual allocation length. Wrapped-SOL tokens increment the first token counter; the tested other mint increments the second.

Rate zero bypasses cooldown. Otherwise `now - last_claimed > claim_rate_limit` must hold; equality rejects and signed subtraction overflow aborts. Empty sweeps still set the timestamp and emit an event. A destination equal to the vault retains its native balance while recording the claimed amount. These are reconstruction observations, not independent vulnerability or exploitability findings.

## Frozen validation

The candidate is **299,376 bytes**, SHA-256 `0f7dcf7c3aaaec9da07a34a9cc614ae376a18ae6136d923c0a98604fa18179b7`. The original is **948,944 bytes**, SHA-256 `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e`. Full-file equality is **false**.

The candidate passes **1,249/1,249** signed LiteSVM differential cases. These compare errors, account data/ownership/lamports, event payloads, inner instructions and return data. Coverage includes all 256 indexes per handler, authority and account constraints, allocation sizes, native/SPL Token/Token2022 transfers, cooldown arithmetic, overflow and destination aliases. Source-location log text and compute consumption are not compared.

The same ELF passes **18/18** real Surfpool comparisons across **36 signed transactions**: 24 successes and 12 expected rejections. The sequence tests actual initialization, a normally signed global-authority update, then a signed System Program deposit and sweep. The created vault and ATA are preserved between steps; assertions verify the deposited million lamports reaches the destination. Other cases cover both token programs, zero balances, cooldown, overflow and typed account rejection.

Surfpool compares errors, account ownership/lamports/data and event payloads. Only the decoded `BuybackVault.last_claimed` field is excluded from account comparison because independent processes use wall-clock time; its raw value and logs are retained. The deterministic LiteSVM tests separately compare inner instructions and return data. These checks do not establish complete program coverage or byte identity.

## Reproduce

Install the environment with `localnet/setup.py`, then run from repository root:

```sh
work/localnet/venv/bin/python scripts/build_partial_candidate.py \
  --manifest localnet/recovery/fees-buyback/crate/Cargo.toml \
  --program pump_fees --artifact-name pump_fees_candidate.so \
  --output work/buyback-draft-build
work/localnet/venv/bin/python scripts/fees_buyback_differential.py \
  --candidate work/buyback-draft-build/artifacts/pump_fees_candidate.so \
  --output work/buyback-differential.json
work/localnet/venv/bin/python localnet/buyback_transactions.py \
  --candidate localnet/recovery/fees-buyback/pump_fees_candidate.so \
  --output work/buyback-surfpool
```

Output directories must be new. The selected Anchor 0.31.1 / platform-tools v1.52 environment is a candidate environment, not proof of original compiler/dependency versions. The Surfpool runner uses pinned 1.6.1 on loopback ports 20001/20002 and stops its disposable instances after testing.
