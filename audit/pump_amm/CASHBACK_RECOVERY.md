# PumpSwap cashback recovery

`claim_cashback` transfers the complete token balance of the canonical accumulator
vault to a token account of the same mint owned by the user. The destination need
not be the user's ATA. The caller does not need the user's signature; the transfer
can only go to that user's checked token account. The ordinary transaction payer
signs the local fixtures. No privileged signer injection or live RPC is used.

The user accumulator is bound to the user key through its PDA seeds. The stored
user field is not separately required to equal that key. The quote mint and token
program are typed, the source is the canonical vault ATA, the destination's mint
and authority are checked, and both the event authority and program account are
validated before executing the handler.

The handler reads the clock, skips token CPI when the source balance is zero,
otherwise performs a checked token transfer, then adds the full transferred amount
to `total_cashback_claimed` with error 6023 on overflow. It leaves `cashback_earned`
unchanged and emits the log event and event CPI even when the amount is zero.
Failure of the checked addition rolls back the earlier transfer.

The original wrapper is at 0xed210, body at 0x5b5b8 and account-context decoder at
0xcc658. The retained static evidence and ordinary signed fixtures informed the
recovery. The first draft differed on 13 of 146 cases: 12 were caused by executing a
zero-amount token CPI, and one by deferring the program-account check until event
CPI. Exact draft sources, executable, build log and mismatch receipts are retained.

The final bounded suite compares 146 cases, including zero and large amounts,
claimed-counter overflow, legacy/Token2022 token programs, WSOL and non-native
mint fixtures, malformed account data/owners, missing accounts, readonly accounts,
incorrect destinations and program accounts, and trailing instruction bytes.
It compares recorded account state, errors, events, inner instructions and signed
transaction bytes. Raw logs are retained but compute/source-location differences
are excluded from equality. Synthetic state does not establish production
reachability; arbitrary Token2022 extensions and every account alias are not
exhaustively covered.

The combined 32-handler candidate passes 14,635 comparisons across 21 suites. Six
published AMM handlers remain absent. Whole-file byte equality, historical-source
attribution and a full original-program security audit remain unresolved. The
security review frozen at 329fc44 excludes this addition.
