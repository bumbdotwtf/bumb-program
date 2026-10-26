# PumpSwap account extension recovery

`extend_account` recognizes four raw discriminators and grows their allocations:
Pool to 301 bytes, GlobalConfig to 949, UserVolumeAccumulator to 137, and
GlobalVolumeAccumulator to 600. Unknown discriminators or fewer than eight bytes
return 6027. The account must be owned by the AMM (Anchor ConstraintOwner, 2004),
and the payer is an ordinary mutable signer. A canonical PDA is not required.
The body is not deserialized; existing bytes are preserved and new bytes are zero.

At or above the target size, the instruction returns without a transfer or event.
For growth it charges `rent(new_size) - rent(old_size)` regardless of the account's
actual balance, transfers that delta from the user, reallocates, then emits
`ExtendAccountEvent` both as a log and self CPI. Already overfunded accounts still
pay the size-based delta. Initially underfunded accounts may remain underfunded
and fail transaction rent checks even after the handler succeeds. This behavior
is reproduced rather than replaced with a balance-based top-up.

The 317-case suite compares errors, committed bytes/lamports/owners, exact System
and self-event CPIs and event bytes. It covers all supported and unsupported
captured account discriminators, short and malformed bodies, size boundaries,
signers, writable privileges, substituted accounts, owner checks and balances
from absent/underfunded through overfunded. Tests use ordinary signatures in local
LiteSVM. No network transaction is sent, and the original ELF never enters the
candidate build. This remains bounded behavioral recovery, not whole-program
or byte-identical equivalence.

## Frozen checkpoint

`repro/pump_amm/extend-twenty-two/` contains the clean ELF, source/test snapshots,
build provenance and thirteen reports. Candidate size is 699,568 bytes, SHA-256
`5bb450a2f3046a25d230eace6b5555e77a886a1f0fcae4ec0016e17ed57bf187`.
All 11,891 cases have zero observed mismatches. Whole-file equality with the
10,485,715-byte deployed original fails, with the first difference at offset 25.
Sixteen IDL handlers remain absent.
