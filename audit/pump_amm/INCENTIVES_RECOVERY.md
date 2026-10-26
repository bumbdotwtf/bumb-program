# PumpSwap incentive recovery

The reconstruction adds `sync_user_volume_accumulator`,
`admin_update_token_incentives` and `claim_token_incentives`. The captured PumpSwap
binary and published IDL supply the account layouts, instruction arguments and
behavioral reference. The clean main-source candidate implements 31 of 38 IDL
handlers; seven handlers and historical build identity remain unresolved.

## Recovered behavior

Synchronization resets the claimed-token total and its initialized flag only when
both the current timestamp and last update precede the incentive start. It emits
an event only when the numeric claimed total changes.

Incentive administration requires the stored admin signature, canonical global
accounts, and a typed mint/token program. It creates the canonical incentive ATA
when needed. Schedule changes validate start/end times, the 30-day range and active
day ordering before changing daily supplies. Future-volume clearing starts strictly
after the start timestamp and requires an end day later than the current day.
Zero start/end arguments retain the existing schedule; zero supply skips supply
replacement. Arithmetic overflow, invalid signed-to-unsigned conversion and index
bounds preserve the observed rejection behavior rather than defining a new policy.

Claims use the canonical user and global accumulators, a matching incentive mint,
and canonical destination/vault token accounts. The destination user is not a
required transaction signer; the ordinary payer signs any needed ATA creation.
The shared updater resets pre-start claim fields, converts time indices, accrues a
completed day's proportional reward, and then transfers unclaimed tokens through
the captured token program. Eligibility compares day quotients, including after
schedule end. A zero claim returns early after the accumulator update.

Direct original-code ranges are retained for the shared claim updater
`0x6d408..0x6db20`, administration updater `0x6db20..0x6f3c8`, and end-day helper
`0x6f3c8..0x6f4b0`. These static observations corrected 25 differences in an earlier
draft: 16 administration cases and nine claim cases. Failed draft receipts and the
exact build 03 source snapshot remain in the package.

## Validation and limitations

The new suites contain 222 synchronization, 668 administration and 807 claim cases.
Each side verifies ordinary signatures from deterministic local test-owned keys;
there is no privileged signer injection or live RPC. Fixtures include timestamp,
period and amount boundaries, token-program variants, ATA creation, account
constraints, malformed data and arithmetic failures. For these cases the harness
compares errors, pre/post account state, events, inner instructions, return data and
transaction bytes. Raw logs are retained but not compared because compute usage
and source locations differ. Synthetic configurations deliberately assign admin to
an ordinary local key and do not establish production reachability.

The complete current regression has 14,489 cases across 20 suites. Existing suites
retain their documented comparison limits. This evidence does not establish
exhaustive handler/context parity, whole-program equivalence, historical source
attribution or security. The source review frozen at 329fc44 excludes these changes.
The candidate remains 926,096 bytes, SHA-256
`64eb043633e3c0cbac05a16ebb0f1160f0123f7731d038e8faf2b59794e57ed6`;
whole-file equality with the captured program is false.
