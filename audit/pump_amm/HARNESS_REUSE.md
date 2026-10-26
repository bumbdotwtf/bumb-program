# Reusable local SBF harness validation

The liquidity and v2 differential runners now cache program compilation separately
for each binary path. Before every case the wrapper restores all accounts changed
by setup and all writable transaction accounts, including the transaction payer.
Missing accounts are reset to zero-lamport empty System accounts, which LiteSVM
presents as absent. Transaction history remains disabled. Each runner resets its
clock explicitly. The runners and tested binaries are fixed for one process.

`PUMP_AMM_FRESH_VM=1` retains the original fresh-VM path for independent checks.
No instruction cases or assertions were removed. The validation receipt at
`repro/pump_amm/reusable-harness/validation.json` compares all 1,550 complete case
records against the immutable `trade-seventeen` fresh-VM receipts. Every original
and candidate result matches, including logs, errors, event bytes, exact inner
CPIs, account data, lamports and ownership. Candidate SHA-256 is
`4e509520c9f6cda114578f246e01fafc88bb2579ef0b913b1212543194153dfb`.

This change affects testing speed only. It adds no reconstructed handler and does
not alter the established behavioral or byte-equality limits of checkpoint 17.
