# PumpSwap protocol and creator fee sweeps

`sweep_protocol_fee` and `sweep_creator_fee` are implemented against captured
original behavior. Both are callable by an ordinary signed payer, who pays any
pool resize or recipient ATA creation costs. There is no reconstructed admin
requirement for these instructions.

The shared context validates pool quote-mint/vault relationships and the
recipient's associated token address. Both reject a zero recipient with 6013.
Normal protocol recipients are selected by binary search of the configured
array; the Mayhem path checks the primary reserved recipient and the seven
additional reserved recipients directly. Unsorted normal arrays can therefore
reject a key that is present. Creator sweeps require the AMM `creator_vault` PDA
for the stored coin creator, including a zero stored coin creator when that PDA
is supplied. Incorrect creator recipient uses ConstraintSeeds (2006).

Legacy pool allocations are grown to 287 bytes with a rent top-up when needed.
The sum of both accrued fee buckets must fit u64 and the quote vault balance must
cover that sum, even when the selected bucket is zero. A zero selected bucket
then returns without transfer, ATA creation or event. For a nonzero bucket,
virtual reserves plus the swept amount must fit i128 before any token or ATA CPI.
Missing recipient ATAs use CreateIdempotent; existing token data proceeds to the
captured token program's checks. The pool signs a TransferChecked for the entire
selected fee bucket. Virtual reserves increase by that gross amount and the
bucket is cleared. The other fee bucket remains unchanged.

`SweepPoolFeeEvent` records the gross amount and bucket (protocol 0, creator 1).
Quote-token transfer fees reduce the recipient's net credit without reducing the
event amount or cleared bucket. A self-transfer requires the source token account
authority to equal the pool; otherwise 6087 is returned before the token CPI.
Global buy/sell/deposit/withdraw disable bits do not disable these sweeps in the
tested cases.

The 254-case suite uses the captured classic SPL Token, Token2022 and ATA ELFs.
It compares exact inner CPIs and event bytes, errors, and committed data/lamports/
owners for the involved accounts. Coverage includes both buckets, zero and
boundary balances, normal/reserved recipient selection, malformed/substituted
accounts, signers and writable privileges, legacy allocation/rent, transfer-fee
extensions, arithmetic overflow and self-transfers. This is bounded behavioral
validation, not an exhaustive proof or byte-identical recovery. Original ELF
bytes are not linked into the candidate, and all execution is local.

## Frozen checkpoint

`repro/pump_amm/sweep-twenty-one/` contains the clean candidate, source and test
snapshots, build provenance, whole-file comparison and all twelve receipts.
Candidate size is 687,616 bytes, SHA-256
`039f16ea33468d32af7f84a2b0e346183a8632dce5e5068491c2efaf058fd301`.
All 11,574 cases have zero observed mismatches. The 10,485,715-byte original still
fails whole-file equality, beginning at offset 24. Seventeen IDL handlers remain
absent from this checkpoint.
