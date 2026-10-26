# PumpSwap administrative recovery checkpoint

This is a partial, independently compiled implementation of twelve of the 38
published instructions. It is not the historical source, a complete security
audit, or a byte-identical program. Unknown instructions use Anchor's fallback;
they are not silently accepted or represented by successful empty handlers.

Implemented instructions:

- `disable`: replace bits 0–4 individually while preserving bits 5–7; emit both
  the log event and the signed event CPI.
- `update_admin`: assign the unchecked new account's public key, including a zero
  key; emit the old admin and new admin through both event paths.
- `toggle_mayhem_mode`: reject unchanged state with 6043; change the bool otherwise.
- `toggle_cashback_enabled`: reject unchanged state with 6051; change the bool otherwise.
- `toggle_boost`: require a nonzero boost authority (6005), then assign the bool.

- `update_buyback_config`: optional basis points up to 10,000; optional exactly
  eight remaining recipient accounts, each nonzero and pairwise distinct. Preserve
  supplied order. Invalid basis points precede recipient errors. No event.
- `update_fee_config`: independently limit LP/protocol/creator fees to 1,000 bps
  each; require eight nonzero, strictly sorted, unique protocol recipients. Set
  the admin-set-creator authority without imposing a nonzero requirement. Emit
  the event through both paths.
- `set_boost_authority`: extend a legacy global config to 949 bytes and top up
  rent via System Program if needed, then store the new key, including zero.
  Emit old/new authorities through both event paths.
- `update_creator_fee_config`: same resizing and rent handling; assign the bool
  and u64 maximum, including zero and u64 max. No invented fee cap is imposed.
  Emit through both event paths.
- `set_reserved_fee_recipients`: require the canonical global-config PDA and at
  least eight remaining accounts. Use the first eight, reject zero keys, preserve
  order and accept duplicates. Set the supplied whitelist key and emit recipients.

The ten configuration handlers require a signing admin related to the writable GlobalConfig.
A wrong admin returns custom error 6005, not Anchor's generic HasOne error.
The event-bearing account contexts also check the event PDA even for the two
simple toggles that emit no event. `toggle_boost` takes just two fixed accounts.
The tested noncanonical config address is accepted when its owner, serialized
state and admin relationship are valid. This is observed behavior, not a finding.

Original binary anchors: disable wrapper `0xe1508`, handler `0x17960`;
update_admin wrapper `0xe1cc0`, handler `0x1bdb0`; toggle_mayhem_mode handler
`0x1bb00`; toggle_cashback_enabled handler `0x1b510`; toggle_boost handler
`0x1b7c0`. The original GlobalConfig deserializer at `0x5e7xx`/`0x5e978`
checks legacy payload lengths 899, 932, and 941 after the discriminator: total
account lengths 907, 940 and 949. The candidate preserves the three layout
boundaries, rejects an invalid discriminator/minimum length as InvalidAccountData,
and forwards malformed bools as BorshIoError. Short writable legacy accounts can
execute the handler and emit events before failing to serialize the larger state;
transaction rollback prevents the state change from committing. The resize-enabled paths compare the complete reserialized state, including
legacy fields defaulted to zero; lengths 907, 908, 939, 940, 941 and 948 are covered.

The differential harness tests all 256 preexisting flag bytes against all 32
requested flag combinations, authority/signature/owner/writeability errors,
noncanonical config addresses, event/program substitution, malformed arguments,
short dispatch, legacy layout boundaries, invalid bool fields, administrative
key replacement and toggle transitions. It compares committed config bytes,
transaction error codes, log-event payloads and rollback. It does not require
compute-unit counts or source-location text to match and does not assert an
exact inner-instruction trace. Resize tests additionally compare payer, admin and
config lamport deltas, covering genuine System Program transfers and rollback. These are bounded behavioral checks, not proof
of all possible inputs or original compiler identity.

## Dependencies and limits

The candidate pins Anchor 0.31.1. Anchor 0.30.1's short-dispatch behavior differs
from the captured originals; 0.31.1 is a behavioral candidate, not a proven
historical version. Cargo.lock pins the independently rebuilt dependencies,
including solana-program 2.3.0, solana-cpi 2.2.1, solana-pubkey 2.4.0 and Borsh
0.10.4/1.8.1. Platform-tools v1.52 is selected for this partial full-program build.
The recovered function and ELF comparisons still differ from the original.

The twelve-handler checkpoint paths use Clock, signed self-CPI for events, and System Program
transfer CPI for rent top-ups during legacy account resizing. Those twelve handlers do not
exercise token/Token-2022/ATA transfers, Pump/Fees pricing CPI, transfer-fee or
transfer-hook extensions, token authority checks, donations, migrations or
multi-hop trading. At that checkpoint those dependencies remained required for 26 other handlers.
The subsequent liquidity checkpoint below adds token transfer coverage.
Original dependency captures and the imported signed trading fixtures are available
for subsequent original-versus-rebuilt tests; their presence is not candidate
acceptance evidence.

No confirmed vulnerability is claimed. Synthetic accounts and authority replacement
are test fixtures; they do not establish control of production state or keys.


## Versioned checkpoints

`repro/pump_amm/admin-five/` preserves the earlier five-handler checkpoint.
`repro/pump_amm/admin-ten/` preserves the earlier ten-handler clean build,
source/test snapshot, separate complete case reports and their hashes. The
candidate binary is compared unmodified with the complete original payload;
length mismatch and differing instruction bytes remain explicit. Nothing in a
passing bounded suite changes that whole-program mismatch.

The ten-handler checkpoint has **9,311** total SBF differential cases
and zero observed mismatches across all five suites on the same candidate ELF.


## Accumulator initialization and closure

The twelve-handler checkpoint adds `init_user_volume_accumulator` and
`close_user_volume_accumulator`. Initialization is idempotent (`init_if_needed`),
allocates 137 bytes, stores the requested user and preserves existing volume/claim
fields. A payer may initialize for another user without that user's signature.
The initializer validates the PDA and existing allocation size. Closure requires
the user's signature and derived accumulator PDA, emits stored totals, refunds
all account lamports to the user and closes the account. It does not require the
stored user field to match, nor require unclaimed/token/cashback counters to be
zero; those are explicitly probed synthetic states, not a vulnerability claim.
Both instructions emit log and self-CPI events. Additional tests cover prefunded
System-owned account allocation/assignment, existing accounts, malformed bools,
wrong owner/PDA, unsigned close and allocation boundaries. The test uses a fixed
nonzero Clock timestamp to distinguish initialization events from preserved state.

`repro/pump_amm/admin-twelve/` pins this clean build and all six suites on the
same candidate ELF: **9,387** cases with zero observed mismatches. The ten-handler
checkpoint remains a separate earlier artifact. Full byte identity remains false.


## Liquidity checkpoint

`repro/pump_amm/liquidity-fourteen/` adds deposit and withdraw to the same clean
full candidate and pins all seven suite receipts: **10,067** cases, zero observed
mismatches. Its 680 liquidity cases additionally compare complete involved account
state and exact inner CPI instructions against the captured original, running the
captured SPL Token and Token2022 binaries. Details and remaining dependency limits
are in `LIQUIDITY_RECOVERY.md`. The remaining 24 handlers are absent; whole-program
byte identity remains false.

## V2 trading checkpoint

`repro/pump_amm/trade-seventeen/` adds `buy_v2`, `sell_v2`, and
`buy_exact_quote_in_v2`, with **10,937** aggregate cases and zero observed
mismatches across eight suites on one clean candidate ELF. The v2 suite includes
870 cases with exact inner CPI payload and involved account-state comparisons.
See `TRADE_V2_RECOVERY.md` for recovered behavior, dependencies and limits.
Twenty-one handlers remain absent and complete byte identity remains false.
