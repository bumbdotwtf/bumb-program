# Volume-account lifecycle recovery

The next partial Pump source checkpoint adds `init_user_volume_accumulator` and `close_user_volume_accumulator`. Initialization allocates 137 bytes, stores the supplied user, and emits the payer/user/timestamp event through log and self-CPI. It uses Anchor's `init_if_needed`: repeated initialization preserves existing counters, while updating the stored user to the supplied PDA user. Prefunded system accounts follow the normal allocate/assign flow. The payer signs; the user does not need to sign initialization.

Closure requires the PDA user's signature and sends the account's lamports to that user. The captured original closes accounts even when unclaimed-token or cashback counters are nonzero, and does not compare the stored user field against the signer separately from the PDA constraint. The recovered source preserves these observed behaviors. Closure therefore discards those counters; this is a behavior observation, not operational advice.

The 66-case differential suite covers ordinary signed initialization/closure, repeated and prefunded initialization, wrong stored user, nonzero counters, rent/account-size boundaries, malformed booleans, owner/discriminator/PDA errors, readonly accounts, signature failures, missing accounts, and trailing argument bytes. It compares entire account state, balances, errors, raw event payloads, and complete inner instructions. The unsigned-payer test uses a different transaction fee payer so the message does not implicitly make the instruction payer a signer.

These lifecycle handlers do not implement volume synchronization, incentive claims, or the still-missing trade/reward branches. All main-program ELF equality claims remain negative.
