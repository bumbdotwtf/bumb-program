# Partial Fees admin CTO recovery

## Verified caller and authority

The official captured Pump IDL exposes `admin_cto`, discriminator `7d7ed6864de5bc59`. Its ordinary signer is `admin_set_creator_authority`, constrained against Pump Global.admin_set_creator_authority (serialized bytes418..450), not Global.authority (bytes9..41). It accepts `is_holder_reward: Option<bool>`, `creator_fee_bps: Option<u64>`, `new_creator: Option<Pubkey>`.

Static inspection of captured Pump SHA-256 `7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d` identifies wrapper0x12da00 → call0x12dfc0 to handler0x22a10 → call0x27488 to CPI helper0x116718. The helper loads Fees admin_cto_sharing_config discriminator `3c64909c408ab625` at0x1167d0. `static_analysis.py` is a read-only over-approximate control-flow tool. Its secondary route through admin_set_idl_authority/shared dispatch is not asserted to be a legitimate equivalent caller; no such route was executed.

After parent review, the fixture executed **only** captured Pump admin_cto transactions. Pool authority is the canonical `[b"pool-authority", mint]` PDA under Pump and **nonsigner at the transaction boundary**. PAYER and AUTH are ordinary test-owned keys, and signatures are verified. Captured Pump signs its own PDA seeds for the genuine Fees and AMM CPIs. No program was patched to manufacture signer privileges; no signature checks were disabled; no direct privileged Fees call or live write was made.

The passing setup has synthetic Global.admin_set_creator_authority=AUTH, current curve creator=sharing-config PDA, a valid sharing state and matching synthetic AMM pool/global config. The top-level account mapping follows the official Pump IDL exactly. Captured Token and ATA dependencies are loaded unchanged. `Some(new_creator)` and holder conversion with `new_creator=None` both reach Fees successfully. The holder path uses the captured Global holder-reward-enabled setting.

## Recovered Fees behavior

- `Some(admin)` resets sharing state to version2, Active, admin=the supplied pubkey, admin_revoked=false, and exactly one shareholder with10000bps.
- `None`, reached through legitimate Pump holder conversion, resets to version2, Paused, zero admin, admin_revoked=true, and an empty shareholder vector.
- Old versions0/1/2/3/255, paused status and prior revocation do not prevent reset. Old shareholder counts/weights are preserved in the reset event but replaced in state. `ResetFeeSharingConfigEvent` emits timestamp, mint, sharing PDA, old admin/shares, new admin/shares, old/new versions via both normal and event CPI emission.
- Tested Fee-layer failures include malformed config discriminator3002, malformed status/revoked/serialization3003, stored bump mismatch2006, and mint mismatch6007. A too-small empty allocation can reach serialization failure when the new single shareholder will not fit.
- Pump rejects wrong ordinary admin6000, missing new creator outside holder conversion6089, conflicting holder/new-creator arguments6090, zero new creator6030, and several wrong account derivations before calling Fees. These are caller evidence, not isolated Fees context evidence.
- Some draft context checks are IDL-based and not independently isolated because the genuine Pump caller already enforces them. **No claim of exhaustive direct-call context equivalence** is made. The standalone candidate covers this legitimate tested call path, not the entire Fees program.

## Validation

**63/63** signed LiteSVM original/candidate cases match errors, all recorded before/after state and balances, event bytes, inner instructions and return data. **50/63** original cases reach Fees admin_cto_sharing_config; remaining rejection/control cases are intercepted by Pump. The candidate is loaded only at the Fees ID; Pump, AMM, Token and ATA stay captured originals.

Pinned offline Surfpool1.6.1 independently passes **12/12 cases,24 signed submitted transactions**, with no mismatches or unexpected original errors. Includes Some/None, multiple old shareholders on both paths, version0, paused/revoked state, malformed config failures and ordinary wrong authority. All message/fixture account data/owners/lamports/flags, event payloads and returns compare; only decoded event timestamps and intentionally different Fees executable bytes are excluded. Raw timestamps/logs/transactions are retained.

Candidate240104bytes SHA-256 `5cc0bec18450846a76576ab2fa8802e0068e39ae771119624c6abb53b27092cf`; original948944bytes SHA-256 `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e`. **Full byte equality is false.**

Source and receipts are frozen at `localnet/recovery/fees-admin-cto`. Maintained runners are `scripts/fees_admin_cto_differential.py` and `localnet/admin_cto_transactions.py`. No main program source changes or commits were made in this lane.

## Package and reproduction

This package is a partial handler recovery, not a deployment replacement. Frozen Anchor0.31.1 source contents match the hashes in `build-comparison.json`; the original clean build path was `work/fees-admin-cto-recovery/crate`, not this copied review directory. Build command, actual selected toolchain/compiler/SDK hashes and byte comparison are recorded. `build.log` retains build output. `differential.json.gz` contains63 cases; `surfpool-transactions.json.gz` contains12 cases and their submitted transactions; `surfpool-fixtures.json.gz` contains exact fixture inputs. `manifest.json` hashes all package files and the maintained runners.

Run from repository root with new output paths:

```sh
work/localnet/venv/bin/python scripts/fees_admin_cto_differential.py --candidate localnet/recovery/fees-admin-cto/pump_fees_candidate.so --output work/fees-admin-cto-recovery/recheck.json
work/localnet/venv/bin/python localnet/admin_cto_transactions.py --candidate localnet/recovery/fees-admin-cto/pump_fees_candidate.so --output work/localnet/admin-cto-recheck
```

Surfpool starts offline on loopbackRPC20011/WS20012 and shuts down. Event normalization verifies emitting program and discriminator, then zeros only the timestamp at offset8 for Pump AdminCtoEvent, AMM AdminCtoPoolEvent and Fees ResetFeeSharingConfigEvent. All raw event bytes remain available in logs. Program executable bytes are retained as hashes/lengths rather than repeated in every account snapshot; only the Fees program's intentionally different hash/length is excluded from comparison.
