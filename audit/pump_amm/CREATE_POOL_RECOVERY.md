# PumpSwap pool creation recovery

The eighteenth implemented handler is `create_pool`. This is a behavioral source
reconstruction, not the historical source or a byte-identical program. The direct
suite has 246 signed local cases; the migration suite adds 37 calls through the
original Pump program and its authentic PDA signer. Both execute the captured
classic SPL Token, Token2022 and Associated Token Account programs.

## Recovered behavior

- Pool allocation is 287 bytes, seeded by `pool`, index, creator and both mints.
  LP mint is a Token2022 mint with nine decimals, authority set to the pool, seeded
  by `pool_lp_mint` and pool. User LP ATA is initialized; pool vault ATAs use
  `init_if_needed` and existing balances participate in initial liquidity.
- Transfers use mint decimals and the supplied token interface programs. Initial
  liquidity is integer square root of the product of final vault balances. Pool
  supply includes 100 permanently locked LP units; minted user supply excludes
  those 100. Initial liquidity below 100 fails and rolls back all account creation
  and token transfers. Zero requested base or quote fails before the transfers.
- Classic mints are accepted. The reconstructed Token2022 extension check accepts
  metadata pointer and token metadata; transfer fees, mint close authority,
  default account state, non-transferability, interest-bearing configuration,
  permanent delegate, transfer hook and group pointers were rejected in probes.
  This does not establish coverage of every future Token2022 extension.
- Global creation-disable flag, Mayhem enable flag and cashback enable flag are
  checked. Mayhem and cashback require a creator matching the original Pump
  `pool-authority` PDA for the base mint. Configurable creator fee and edit flag
  likewise require that canonical creator, after token transfers. Canonical
  creator fee inputs tested across the full u64 range are retained without a
  global maximum clamp in these fixtures.
- Noncanonical pools store a zero coin creator while their event retains the
  requested coin creator. Noncanonical holder-reward input is ignored. Canonical
  creation retains creator, cashback, Mayhem, fee/edit and holder flags.
- Optional trailing booleans default false at EOF. The optional u64 consumes
  available bytes and pads a truncated value with zeros. Invalid boolean values
  fail Anchor instruction deserialization. These custom wrappers are not Borsh
  `Option<T>` values with a presence tag.

## Validation and boundaries

Direct cases compare errors, event bytes, exact inner CPI instructions and
committed account data, lamports and owners. They cover initialization, amounts,
LP lock boundary, index range, optional/truncated payloads, signer/writable and
substituted-account constraints, existing vault balances, frozen/malformed token
accounts, mint fields and token extension variants.

The migration runner verifies the saved transaction signature, then disables only
historical blockhash freshness in LiteSVM. The original Pump ELF supplies the
actual PDA signature. Modified before-account data is synthetic and identified
per case. Missing-boost transactions compare the successful `create_pool` call
and later rollback. Mayhem cases bypass boost and compare complete committed
migration account states. The eighteenth checkpoint omits the non-Mayhem `init_boost` path. The nineteenth
checkpoint adds it with separate fully committed migration tests documented in
`BOOST_RECOVERY.md`. This creation suite alone does not claim full migration
support or whole-program equivalence.

Original deployment bytes are never linked into the candidate. All original
program use is confined to the independent execution side and dependency caller.

## Frozen checkpoint

`repro/pump_amm/create-eighteen/` contains the independently rebuilt ELF, source
snapshot, compiler/build comparison and ten compressed differential receipts.
The exact candidate is 631,768 bytes, SHA-256
`22535cb9a88fd0201359a9d53e1580df845ee4f0d09805915f21ef28a16501a4`.
All 11,220 cases have zero observed mismatches. The deployed ELF is 10,485,715
bytes; whole-file equality fails, beginning at offset 24.
