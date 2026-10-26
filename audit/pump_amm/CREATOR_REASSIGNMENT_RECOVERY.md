# PumpSwap creator reassignment recovery

Three additional instruction bodies are reconstructed: `migrate_pool_coin_creator`,
`set_coin_creator` and `admin_cto_pool`. These extend the 25-handler candidate to
28 implemented handlers. Ten published IDL instructions remain absent; full binary
identity, complete context equivalence and a security sign-off remain unestablished.

`migrate_pool_coin_creator` checks the canonical pool PDA using a freshly derived
bump, rather than the stored bump byte. Its Fees-owned sharing account must be the
mint's canonical sharing PDA, name that base mint, and have an admin equal to the
pool's current coin creator. The body rejects holder-reward pools and unswept creator
fees, replaces the creator with the sharing-account key, then emits log and CPI
events. Tested stored sharing versions, paused status and revoked flags do not add
a rejection. This observation does not establish that every injected configuration
is reachable through production writers.

`set_coin_creator` validates both a Metaplex metadata account and the Pump bonding
curve even when one will not supply the creator. It checks the pool's creator against
Pump's base-mint-derived pool authority before returning without change for an
already populated coin creator. Otherwise the first metadata creator is selected
when a creator vector is present; its verified flag and share do not change the
selection. If the vector is absent, the curve's creator is used. A present empty
vector panics in the tested original and candidate. The pool index is not part of
this body-level canonical-creator check. The two source branches emit distinct
Metaplex/curve events.

`admin_cto_pool` is reached through the captured Pump `admin_cto` implementation.
All top-level transactions use ordinary test-owned signatures; the genuine Pump
program supplies its own pool-authority PDA signature inside CPI. The recovered
context binds that signer to the pool base mint. The body extends legacy pools to
287 bytes, funding any rent shortfall from the payer. It requires the pool creator
to equal the authority, rejects Mayhem pools, and prevents removing holder-reward
mode. Enabling holder rewards requires the derived holder-rewards creator and
clears cashback before optional creator-fee validation. Optional fees reject WSOL
and USDC quotes, remaining cashback mode, disabled configuration and values outside
1 through the configured maximum. Creator fees must be swept before the change.
The handler records the new creator/mode/optional fee, disables subsequent fee
editing, and emits old/new values in the event.

The new suites contain 327 direct migration/setter cases and 159 Pump-to-AMM CTO
cases. Of the latter, 140 reach `AdminCtoPool`; 19 reject in the captured upstream
Pump or its earlier CPI, so those 19 do not independently validate AMM context
checks. Cases compare errors, relevant complete account states and balances,
event bytes, return data and inner instruction records. Raw normally signed
transactions are retained. They cover synthetic version/length/owner/PDA variants,
metadata selection, no-op behavior, quote/fee boundaries, holder conversion,
legacy resizing and rollback. Signer verification stays enabled throughout.

The full 17-suite regression also reruns the prior 12,306 cases, for 12,792 total
original/candidate comparisons with zero observed mismatches. This is bounded
behavioral evidence; it does not establish every downstream context independently,
all metadata variants, all combinations or whole-program equivalence. No mainnet
mutation or transaction broadcast was performed.

The candidate continues to use platform-tools v1.52 and Anchor 0.31.1; the lockfile
adds the Anchor SPL metadata feature with `mpl-token-metadata` 5.1.1 and
`num-derive` 0.3.3. These are candidate dependency choices, not historical attribution.
The package retains source, harnesses, build provenance and failed-draft evidence.
Original executables were read only after compilation for comparison and were not
compiler inputs. The static security review frozen at `329fc44` does not cover
these newly reconstructed bodies.

The frozen main-source candidate is 849,040 bytes, SHA-256
`21d30fb50cb0cb7c701d16b9d2be3bbb2f19baf6f6ebad3254f7ac51ffe19742`.
See `repro/pump_amm/creator-twenty-eight/manifest.json` for exact suite counts and
file hashes. All complete-file comparisons remain different.
