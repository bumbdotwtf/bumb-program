# AMM multi-hop recovery checkpoint

The main-path candidate adds `multi_hop_swap` to the published AMM36 source. All 25 suites pass against the same clean v1.44 executable: 17,462 cases, including 735 new route comparisons. This is 37 of 38 AMM IDL instruction bodies. `create_config` remains missing because its fixed administrator cannot be manufactured as a transaction signer. Its future runtime evidence must use legitimate historical signed transactions. No live transactions, signature bypass, or executable/header edits were used.

The source build uses the existing validated v1.44 compatibility lock graph. That compiler/lock choice is not evidence of the historical build graph. Original whole-file and ELF-extent equality remain false.

## Recovered behavior

The fixed context validates the user signer, both token interface accounts, AMM configuration and Fees configuration PDAs, initializes the user volume accumulator if absent, and binds token, System, event and Pump program accounts. Pump global/fee/event accounts are passed to the actual captured Pump program when a curve leg is present.

Remaining accounts form groups of five: base mint, quote mint, pool or bonding curve, base vault, quote vault. The route scans mint continuity and enforces one direction for every leg. The quote side wins when both supplied mint keys are equal. Pool-owner classification and AMM leg parsing occur during execution, so a later malformed leg can follow emitted events from an earlier leg before transaction rollback.

AMM legs require canonical Pump pool creators and reject cashback and Mayhem pools. They select token programs by mint owner, extend old pool layouts, and validate the buyback token recipient at the protocol-fee endpoint. LP and creator fees occur at the base endpoint; protocol and buyback fees occur at the quote endpoint. Intermediate legs have only their selected fee components. Fees are selected inline; the wrapper does not make a Fees-program CPI.

Input tokens move first. The leg reloads its vaults and subtracts the received input to recover pretrade reserves. For AMM-to-AMM legs, the preceding pool signs its actual token transfer; for an input prepaid by a curve CPI, the next AMM leg skips the transfer. Final output moves before the trade event. Buyback tokens come from the pool quote vault. Exact-input fee rounding consumes the residual input after rounded fees; it must not cap that residual at the preliminary fee estimate. Small-input rejection and buyback-overflow timing are bound by the negative comparisons.

Each AMM leg emits the original BuyEvent or SellEvent bytes and self-event CPI, using `multi_hop_swap` for buys. Intermediate user account/reserve fields are zero; endpoint fields describe the real user accounts. Accrued protocol/creator fees and virtual quote reserves update independently on each pool. Final slippage is checked after the route, including a zero net quote result under a 100% transfer fee.

Adjacent Pump curves form one `multi_hop_curve_swap` CPI. The original AMM signs its configuration PDA and, when the source is a prior AMM pool, its actual pool PDA. The candidate performs the same program-derived signing in its own normal execution. Both outer transactions are ordinarily signed by local test-owned keys. The byte flags select protocol and creator fee endpoints. The returned amount and buyback receipt are checked against source/destination balances with native-SOL and alias-account handling; the captured Pump implementation remains unchanged.

## Evidence and limits

The 735 comparisons cover one, two and three AMM legs; individual and grouped curve legs; AMM/curve transitions in both directions; exact CPI/event bytes; committed account bytes and lamports; return data; input serialization; user signatures and a separate payer; malformed accounts and route continuity; fee layouts; reserve arithmetic; and Token-2022 transfer fees on endpoint and intermediate tokens. All fixtures are synthetic local state derived from preserved captured fixtures. This is bounded differential evidence, not exhaustive route, extension, adversarial, economic, or live-network equivalence.

Original-only exploratory receipts are not counted again. Executed differential harness versions are frozen in their own snapshots. Build01 preserves a compile failure caused by an immutable token-account amount field. Builds02–04 preserve their source, executables, logs, and negative receipts: native SOL curve balance checks, tiny-buy rounding, fee residuals, panic CPI order, quote-fee slippage, and same-mint route precedence. Build05 is the passing scratch candidate.

Static excerpts are read-only annotations of the captured original. Principal addresses: dispatcher wrapper `0xe9760`, fixed context `0xb3668`, body `0x3dbc0`, AMM group parser `0xb7df0`, AMM leg `0x40a08`, curve-run CPI wrapper `0x45940`, and exact-input fee helper `0x50f00`. Some exploratory filenames predate their identified roles; addresses and preserved assembly are authoritative.

## Published checkpoint provenance

`repro/pump_amm/multi-hop-thirty-seven` binds the clean main-path build, 18 build inputs, maintained test/helper snapshot, 13 runtime inputs, exact scratch/main executable identity, and the 25 complete differential reports. The executable is 1,177,560 bytes, SHA-256 `5b0bffda1c423cb1989822542086d8dd806ab0f7cd419c3899dc57e58433c848`. All 17,462 unique cases ran against scratch; the 735-case maintained multi-hop harness was rerun from `/tmp` against the identical main executable and produced exactly the same case results. The prior 24 suite receipts are reused only under that whole-file identity.

The original whole-file comparison is false, with the first difference at byte 24 and 655,215 differing positions in the shared length. The independent ELF-extent comparison is also false. The package preserves four earlier unsuccessful drafts, their exact source/build records, and negative differential receipts.
