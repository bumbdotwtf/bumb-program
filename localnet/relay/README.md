# Donation-relay attribution

The captured dependency `RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu` identifies
itself as Donate.gg Donation Relay in its embedded security metadata. The metadata
points to `https://github.com/CherryDevelopmentOrg/daas`; GitHub's API and public
page returned HTTP 404 during this review. That does not prove the repository was
deleted or that its source cannot be recovered. No historical commit is embedded.

The [official integration documentation](https://docs.donate.gg/blockchain/solana-svm)
identifies the same program. The binary's auditor field names Halborn; this is a
publisher claim, not independent verification of an audit or its applicability.

A finalized read-only RPC request retrieved the Anchor IDL account
`6mCmANHqUcqWCLAUtB3DFJSDv14yWPq4wXUzDhdMj3Ge`, owned by the relay program.
The account is derived from the program's empty-seed PDA using `anchor:idl`.
The compressed IDL begins after the eight-byte discriminator, 32-byte authority,
and four-byte compressed length. Raw account bytes, RPC response and parsed IDL
are preserved here. The IDL advertises version **0.6.0** and eleven instructions.
All eleven instruction discriminators match comparisons in the captured program's
SBF dispatcher. This verifies interface correspondence, not original source identity.

[`attribution.json`](attribution.json) records the binary hash, source-path strings,
security metadata offsets and dispatcher addresses. Reproduce the binary analysis:

```sh
work/localnet/venv/bin/python localnet/relay/analyze.py
```

The captured ELF contains 26 local Rust source paths, but no `.comment` section or
exact compiler version string. Compiler and dependency versions remain unresolved.
No source rebuild or security finding is claimed by this attribution work.
