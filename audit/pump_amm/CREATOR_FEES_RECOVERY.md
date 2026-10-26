# PumpSwap creator-fee recovery

Three handlers are recovered: `collect_coin_creator_fee`,
`transfer_creator_fees_to_pump`, and `transfer_creator_fees_to_pump_v2`.
All tests use ordinary signed local transactions with captured token and ATA
programs. The original AMM ELF is only a comparison oracle after compilation.

## Collection

The AMM derives its authority with `[creator_vault, coin_creator]`. The vault
uses associated-token constraints; the receiving token account has explicit
mint, authority and token-program constraints, but need not be an ATA. Anyone
can trigger collection, while the constrained destination receives the funds.
Fee-program ownership of the creator account produces error 6048 regardless
of account data. Empty balances return without CPI or event after constraints.
Nonzero balances transfer the whole vault amount with the derived authority
and emit the gross amount through both event log and self CPI. Token-2022
transfer fees reduce the destination's received amount.

The 148-case differential covers amount boundaries, account substitution and
writability, short payloads, token data lengths and fields, mint and account
owners, Fee-owned creator data, and Token-2022 transfer fee configurations.

## Transfer to Pump

Both variants derive the Pump creator vault under the Pump program with
`[creator-vault, coin_creator]`. The legacy variant only accepts native WSOL.
For native quote, the handler closes the AMM ATA to its own authority, recreates
that ATA using the authority as payer, and transfers every remaining authority
lamport to the Pump creator vault. Extra authority lamports are included in
that final transfer. The preliminary threshold, however, only compares the
ATA's lamports with `rent(165) + max(rent(0) - pump_vault_lamports, 0)`.
Below that threshold the handler succeeds without changing state or invoking
any CPI. Extra authority lamports do not satisfy the threshold.

The v2 non-native path creates a missing Pump destination ATA, paid by the
caller, then transfers the whole quote balance, including a zero-amount
TransferChecked invocation. It leaves AMM authority SOL untouched. Existing
recipient accounts are passed to the token program rather than locally
validated for token authority. Transfer instructions emit no AMM event.

The 267-case transfer differential covers both instruction variants, rent
threshold equality and adjacent boundaries, authority and destination
balances/owners/data, token fields and account lengths, substitutions and
writable privileges, classic and Token-2022 quotes, existing destination token
states, and transfer-fee configurations. It reproduces errors as well as
successful execution.

## Scope and evidence

All fifteen checkpoint suites compare their defined errors, committed account
state and exact CPI/event evidence against the same independently built
candidate. The new suites compare account bytes, owners and lamports, exact
inner instructions, event payloads and returned errors; other logs and compute
costs are not equality criteria. These bounded tests do not establish arbitrary
Token-2022 extension compatibility, complete control-flow coverage, source
identity or byte equality. Thirteen published handlers remain absent. No
network transaction or deployment is performed.

`repro/pump_amm/creator-twenty-five/` preserves the source/test snapshots,
independent build provenance and all fifteen differential reports.

The frozen candidate is 761,696 bytes, SHA-256
`1d50f5e3da23358180e88058254cf09900db841a762305d02607a323a5df0021`. All 12,306 cases across fifteen suites have zero observed mismatches. Whole-file equality fails.
