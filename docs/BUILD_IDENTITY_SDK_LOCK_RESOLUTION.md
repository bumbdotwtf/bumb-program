# SDK lock and named-account resolution audit

The retained integration manifest did not pin its transitive dependency graph. The new passive package at `repro/sdk/locked-client-resolution-20261025/` records an actual npm11.5.1/Node24.5.0 lock-only resolution and 91 authenticated registry archives. It is a newly resolved experiment, not the original deployed program or historical SDK environment.

## Concrete version discrepancy

The manifest pins root web3.js1.98.0. Pump SDK4.3.1 and Pump Swap SDK2.2.0 resolve separate nested web3.js1.99.0 copies. Anchor remains0.31.1, SPL Token0.4.13 and BN resolves5.2.5. The lock contains99 package placements,91 unique archives and196 dependency/optional/peer references. Only node-fetch's optional encoding^0.1.0 peer is absent. Declared ranges and targets are retained; npm semver acceptance has not been independently reimplemented.

## Bounded implementation and verification

An offline Anchor instruction builder supplied19 synthetic keys and constructed ordinary buy23/sell21 named-account lists. Four buy and two sell defaults were derived. Independent standard-library PDA math agrees with Node and saved Solders results; complete IDL order, flags, keys, discriminators and argument bytes agree. All152 loaded CommonJS module files bind to authenticated archives. The4747 materialized regular files were checked before and after. No SDK transaction wrapper, real pool state, remaining-account flow, fee selection, target program, signing or submission was executed. Network/RPC traps recorded zero attempts; this is an inspected process observation, not an operating-system network sandbox proof.

The bigint native binding failed to load and used pure JavaScript. Native dependency identity, npm-ci equivalence, historical graph, unexpanded helper/wrapper sites and real state compatibility remain open. This client result does not close compiler, contract decompilation or whole-binary identity gaps.

Run `python -B repro/sdk/locked-client-resolution-20261025/verify_package.py` for complete package membership/hash checks and passive archive/IDL/PDA verification. Seal: `8a351ec761f71625466144d0c147e1aaa07267df2fbb73b7fd081fec40755ae3`. Three materialization preflight failures remain disclosed; author summaries are distinguished from raw receipts. Contract sources, selected artifacts and status are unchanged by this publication.
