# Authority and reserved-recipient recovery checkpoint

The partial Pump source now implements 12 administrative instructions. The two additions are `update_global_authority` and `set_reserved_fee_recipients`; the existing buy and sell instructions remain partially recovered. This does not establish a complete program or byte-for-byte recovery.

The clean candidate is `repro/pump/authority-admin-candidate.so` (399,160 bytes, SHA-256 `a320082908f8a527865a42f25f748c92541b222d246ed6b6cdde3ea4b41e57df`). `authority-admin-build-comparison.json` records source and compiler hashes and the full-file mismatch against the original. All 1,268 current differential cases pass: 59 new authority cases, 351 configuration, 334 buy, 301 sell, 130 quote-token, and 93 earlier administration cases.

The authority update requires the existing authority's signature, changes the global authority, and emits both log and self-CPI events. The original accepts a zero address or the current address as the replacement; the candidate preserves this behavior. No replacement signature is required. A zero replacement can therefore make future authority operations inaccessible; this is observed original behavior, not a recommended operational action.

The reserved-recipient update requires at least eight remaining accounts and uses the first eight. Each must be nonzero, nonexecutable, and rent exempt. Additional accounts are ignored; duplicate recipients and a zero whitelist PDA argument are accepted. The instruction stores the first recipient separately and the remaining seven in its array, then emits its event through both channels. Readonly authority accounts are accepted by both new instructions.

The new differential suite compares the entire global account, payer/authority balances, errors, raw event payloads, and all inner instruction metadata/data. It probes recipient count, duplicate/zero/executable/data-bearing accounts, rent boundaries, malformed data, owner/PDA/signature/readonly failures, and extra instruction bytes. This bounded coverage does not prove all possible runtime states.
