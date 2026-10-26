# PumpSwap boost initialization recovery

`init_boost` is the nineteenth reconstructed handler. It enables the tested
non-Mayhem migration to execute completely through the original Pump caller and
the candidate AMM. This remains a partial program reconstruction and does not
establish byte equality or support for unrelated migration/trading branches.

The account context checks the global configuration PDA, pool mint/vault
relationships, boost authority PDA (`boost_vault`, pool), and quote-token ATA.
The boost vault uses `init_if_needed`, paid by the signed creator. Account
initialization occurs before handler guards, so an ordinary noncanonical caller
can pay to initialize that ATA even when no boost transfer follows.

The transfer path requires the creator signer to equal Pump's `pool-authority`
PDA for the base mint, boost enabled, and no existing effective virtual reserves.
The effective-reserve predicate combines virtual reserves and accrued creator and
protocol fees. The transfer amount is
`floor(base_vault_amount * quote_vault_amount / 1_000_000_000_000_000)`.
This is a fixed denominator, not the mint's current supply. A zero result or a
result at least the available quote amount is skipped. A quotient outside u64
fails truncation. The pool signs the quote-token transfer, virtual reserves become
the transferred amount, and `InitBoostEvent` contains the Pump bonding-curve PDA
and reloaded remaining quote amount.

The handler entry and arithmetic helper were traced in immutable disassembly at
0x1ef90 and 0x1ecd8 respectively. The arithmetic helper embeds the fixed 10^15
constant. Actual original/candidate execution checks the observed behavior rather
than relying on disassembler target labels.

The 100-case suite covers direct signed account/PDA/ownership/writability and
legacy allocation constraints, existing boost vaults, configuration flags, and
fully committed saved signed Pump migration with synthetic base-vault balances,
curve lamports and mint supplies. The migration transaction signature is verified;
only historical blockhash freshness is disabled. The original Pump ELF supplies
the authentic PDA signer. Unlimited local log capture retains every event, and
comparisons include exact inner CPIs, error outcomes, committed account bytes,
lamports and owners.

These tests do not exercise every Token2022 extension or every possible malformed
state through the canonical signed caller. They do not establish correctness of
`boost_buy_and_burn`, which remains absent. No transaction is sent to an RPC node
or network, and original deployment bytes are not included in the candidate build.

## Frozen checkpoint

`repro/pump_amm/boost-nineteen/` contains the independently rebuilt ELF, source and
test snapshots, compiler/build comparison and eleven differential receipts.
The exact candidate is 661,480 bytes, SHA-256
`1c0f001fb2b5885f922505c59bdb6ca51295458930e80646856bb92981806b5e`.
All 11,320 original/candidate cases have zero observed mismatches. The original
deployed ELF is 10,485,715 bytes; whole-file comparison fails from byte 24.
