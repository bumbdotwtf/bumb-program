# PumpSwap liquidity recovery

`deposit` and `withdraw` are independently implemented from the captured original
ELF, disassembly, and local signed executions. They are part of a partial
fourteen-handler candidate, not a reconstruction of the entire 38-handler program
or a byte-identical binary. The upstream IDL alone was insufficient: its liquidity
events omit the final quote transfer fee field observed in both original event
channels.

## Recovered behavior

Both instructions use `Pool.lp_supply` as their denominator. Deposit rounds base
and quote ratios up; withdraw rounds down. Quote reserves used for pricing exclude
accrued protocol and creator fees, while events report the full token vault
balance. The LP mint's actual supply is separate: withdraw rejects it exceeding
the stored pool supply with `SeedLockViolation` (6067). Zero LP quantities are
accepted. Zero-quantity transfers are skipped, but mint/burn and event CPIs remain.

Base and quote transfers use the mint's owning token program and TransferChecked.
LP minting and burning use Token2022. The test loads the exact captured SPL Token
and Token2022 ELFs, not a mocked transfer handler. Deposits use the user signer;
withdrawals and LP minting use the pool PDA seeds. The user LP token account has
an authority constraint, but base/quote token owner and mint consistency are
normally checked by the invoked token program. Pool has-one failures return
specific AMM errors rather than generic Anchor errors. Self-transfers require the
source token owner to equal the signing authority (6087 otherwise).

Token2022 quote transfer fees are added to the deposit transfer and subtracted
from withdraw proceeds for the slippage comparison. The event's quote amount is
the ratio amount; its final u64 is the transfer fee. Base transfer fees are not
grossed up. These observations are covered by synthetic extension accounts
executed through the captured Token2022 binary, including zero, capped, and 100%
fee settings. They are behavioral observations, not a claim that every token
extension or production mint is supported.

Effective virtual reserves are `virtual_quote_reserves + protocol_fees +
creator_fees`. After token CPIs, deposit adds the floor of effective reserves
multiplied by LP delta divided by the old pool supply; withdraw subtracts the
ceiling. Effective zero skips adjustment. Negative effective reserves fail with
6023. The virtual field itself may be negative when accrued fees offset it.
Withdraw requires the adjustment to fit u64 (6024 otherwise), while deposit
retains a wider intermediate. Failures after token CPIs roll back all account
changes. The fixed test Clock has a nonzero timestamp.

`Pool` uses a custom compatibility deserializer: 211 bytes is the minimum,
legacy appended fields default to zero, malformed booleans return BorshIoError,
and the current serialized fields occupy 287 bytes. Writes to undersized legacy
accounts can fail at serialization and roll the transaction back. The fixture's
300-byte allocation preserves its trailing bytes.

## Verification boundary

The liquidity suite compares all involved persistent account data, owners and
lamports, transaction errors, both event channels and the exact inner instruction
payloads/account indexes. Compute consumption and source-location text are
excluded. Fixtures use synthetic signing keys and balances around a captured
pool snapshot. No transaction is sent to a network.

The candidate does not yet implement pool creation, buy/sell v1 or v2, donation,
fee collection, migration-facing pool creation, reward claims or multi-hop routes.
ATA creation, Pump/Fees CPI, transfer hooks, confidential transfers and every
possible Token2022 extension combination remain outside this acceptance scope.
No confirmed vulnerability or complete security audit is claimed.

The versioned checkpoint is `repro/pump_amm/liquidity-fourteen/`: 680 liquidity
cases and 9,387 prior-handler cases pass against the same clean candidate. The
441,864-byte ELF SHA-256 is
`4d49220701bf36a5d00f236130fd761349627a90425e2d9a39c0989f206b4fdf`.
Its complete original-byte comparison fails, first at offset 25. Source, lock,
toolchain hashes, logs, source snapshot and all receipts are preserved.
