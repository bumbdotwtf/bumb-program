# Social fee handler recovery draft

This standalone partial crate reconstructs `create_social_fee_pda`, `claim_social_fee_pda`, and `claim_social_fee_pda_v2` from signed execution of the captured Pump Fees program. It is a behavioral source draft for integration, not the historical source, a complete Fees implementation, or a byte-identical rebuild.

All fixtures are synthetic local accounts and test-owned signing keys. The tests verify ordinary transaction signatures. No real authority keys or live transactions are used. Original captures remain unchanged.

## Observed behavior

Creation derives a PDA from `social-fee-pda`, the UTF-8 user identifier, and a one-byte platform. It allocates 179 bytes, checks disable bit 1 and a maximum identifier length of 20 bytes. The tested identifiers need not be numeric, and all platform bytes are accepted. An existing nonzero version returns unchanged; version zero is initialized with cleared counters and reserved bytes.

Claims check disable bit 2 and require the configured social claim authority's signature. A cooldown or zero claimable balance returns `None` without a claim event. The first claim bypasses the cooldown when the stored last-claim time is zero. SOL claims retain the rent for a fixed 179-byte account, transfer excess lamports and saturate the lifetime counter. Events use the stored identifier and platform. These observations describe the captured program, not an endorsement of its design.

V2 uses direct SOL claiming when the mint address is wrapped SOL, even when WSOL token accounts have balances. Otherwise it transfers the source token account's full balance with `TransferChecked` using the selected SPL Token or Token2022 program. A missing recipient ATA is created at the claim authority's expense, which requires that normally signing authority to be writable. The official IDL's default readonly authority fails on that creation path. Existing destination token accounts are checked for supported ownership and mint; their internal authority is not independently checked by this handler. Both ATA addresses are constrained to their canonical derivations.

V2's token event reports the recipient's prior token balance plus the transfer amount with saturation. A self-transfer therefore reports a larger calculated balance even though the token balance does not change. The source draft reproduces this observed event behavior. These synthetic cases are reconstruction evidence, not a security impact or exploitability assessment.

## Reproduce

Use the Python environment installed by `localnet/setup.py`, then run from repository root:

```sh
work/localnet/venv/bin/python scripts/build_partial_candidate.py \
  --manifest localnet/recovery/fees-social/crate/Cargo.toml \
  --program pump_fees --artifact-name pump_fees_candidate.so \
  --output work/social-draft-build
work/localnet/venv/bin/python scripts/fees_social_create_differential.py \
  --candidate work/social-draft-build/artifacts/pump_fees_candidate.so \
  --output work/social-create.json
work/localnet/venv/bin/python scripts/fees_social_claim_differential.py \
  --candidate work/social-draft-build/artifacts/pump_fees_candidate.so \
  --output work/social-claim.json
work/localnet/venv/bin/python scripts/fees_social_claim_v2_differential.py \
  --candidate work/social-draft-build/artifacts/pump_fees_candidate.so \
  --output work/social-claim-v2.json
```

LiteSVM tests compare errors, state, balances, events, inner instructions and claim return data. The independent Surfpool tests compare errors and account state while excluding only the last-claim timestamp, because separate processes use their wall clocks. Raw timestamps and logs remain in the receipts. Selected Anchor and compiler versions are candidate build settings; they do not establish the original compiler or dependency versions.

## Frozen results

The 309,808-byte candidate has SHA-256 `10372f4eadf92ba52d838d33df03f30b1e84365fed02f77370ffc6132fab6837`; the original is 948,944 bytes. Full byte equality is **false**. The frozen candidate passes 588 creation, 347 claim-v1 and 627 claim-v2 differential cases (1,562 total). Source hashes match the clean-build receipt; `source-manifest.json` maps the copied paths.

The same candidate passes 16 Surfpool comparisons across creation and claim-v1 (32 signed transactions), including persistent creation, ordinary System transfers, claiming and cooldown retention.

```sh
work/localnet/venv/bin/python localnet/social_transactions.py \
  --candidate localnet/recovery/fees-social/pump_fees_candidate.so \
  --output work/social-surfpool
```

V2 additionally passes 13 Surfpool comparisons (26 normally signed transactions), including native, SPL Token, Token2022, ATA creation, cooldown and expected rejection cases. This runner compares events and return values as well as account state and errors, excluding decoded wall-clock timestamp fields and retaining their raw values.

```sh
work/localnet/venv/bin/python localnet/social_v2_transactions.py \
  --candidate localnet/recovery/fees-social/pump_fees_candidate.so \
  --output work/social-v2-surfpool
```
