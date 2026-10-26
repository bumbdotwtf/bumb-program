# Sharing-update recovery draft

This standalone partial crate reconstructs `update_fee_shares` and `update_fee_shares_v2` from the captured Pump Fees executable. It is a behavioral source draft for integration, not the historical source, complete Fees implementation or byte-identical rebuild. The source hashes match the clean build5 receipt. Selected Anchor 0.31.1 and platform-tools v1.52 are candidate build settings, not proof of original compiler/dependency versions.

All fixtures use synthetic local state and normally signed test-owned keys. Sharing creation runs through the captured original before the candidate is installed. Updates invoke the genuine captured Pump and PumpSwap programs through their actual CPI interfaces; no privileged PDA signer is fabricated. Original captures remain unchanged.

## Observed behavior

Authorization uses the stored sharing administrator. The administrator must not be revoked and the configuration must be active. Before replacing shares, the program distributes existing creator fees to the old shareholders through Pump; graduated coins first transfer creator fees through PumpSwap. The dependency CPIs execute before validation of the new list, so invalid new shares roll back the distributions while retaining their execution traces.

New lists must contain one to ten nonzero shares, without duplicate addresses, summing to10000. Addition uses checked u16 arithmetic. Successful updates replace the shareholders and revoke further administrator updates. V2 supports the curve's configured quote mint and Token2022. Stable-quote remaining accounts are all old shareholder wallets followed by their ATAs; missing recipient ATAs can be created through the dependency CPI.

The recovered source preserves observed error ordering and dependency behavior, including malformed-account handling and allocation/layout boundaries. These are reconstruction observations, not independent vulnerability or exploitability findings.

## Frozen results

The candidate is **305,184 bytes**, SHA-256 `2ffc407f61e3d9a2074f3e20ecd5b128bb53ea83cad5c490de190a2550058fdf`. The original is **948,944 bytes**, SHA-256 `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e`. Full-file equality is **false**.

The candidate passes **417/417** deterministic signed LiteSVM cases, including an independent edge review of version, layout, missing-account and validation-order boundaries. The complete receipt is `differential.json.gz`.

The same ELF passes **19/19** Surfpool comparisons across **38 signed transactions**:26 successes and12 expected rejections. Cases exercise native payouts, two old shareholders and rounding, graduated AMM fee transfers, Token2022, missing ATA creation, and a signed System deposit followed by an update. Invalid new shares roll back both the deposit and the fee distributions; assertions check the old shareholders receive the expected amounts on successful updates.

Surfpool compares exact account data, owners, balances and errors. Event comparison excludes only the first i64 timestamp in the two explicitly recognized IDL events; raw timestamps/logs remain in receipts. Return values are retained but not compared in this runner. The separate deterministic LiteSVM suite compares errors, before/after accounts, event payloads, inner instructions and return data. Neither suite proves complete-program coverage or byte identity.

## Reproduce

Install the environment documented in `localnet/README.md`, then from repository root:

```sh
work/localnet/venv/bin/python scripts/build_partial_candidate.py \
  --manifest localnet/recovery/fees-sharing-update/crate/Cargo.toml \
  --program pump_fees --artifact-name pump_fees_candidate.so \
  --output work/sharing-update-build
work/localnet/venv/bin/python scripts/fees_sharing_update_differential.py \
  --candidate work/sharing-update-build/artifacts/pump_fees_candidate.so \
  --output work/sharing-update-differential.json
work/localnet/venv/bin/python localnet/sharing_update_transactions.py \
  --candidate localnet/recovery/fees-sharing-update/pump_fees_candidate.so \
  --output work/sharing-update-surfpool
```

Output directories must be new. Surfpool1.6.1 binds loopback20021/20022 and its disposable instances stop after testing. The frozen fixtures include raw pre-update accounts following captured-program bootstrap and exact signed transaction bytes. `source-manifest.json` maps the copied source; `artifact-manifest.json` hashes the evidence package.
