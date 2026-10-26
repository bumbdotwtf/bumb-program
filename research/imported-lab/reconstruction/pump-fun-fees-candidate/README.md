# Pump Fees full-interface candidate

`generate.py` creates a fail-closed Anchor/Rust candidate from the pinned
official 31-instruction Pump Fees IDL. It carries declared argument types and
ordered account signer/writable flags. Every handler currently returns an
explicit unsupported error. PDA, owner, rent, CPI, fee arithmetic, account
state, and error precedence are **not** reconstructed. This project must not
be deployed as a replacement.

Its purpose is a reproducible SBF build and whole-ELF comparator for the
byte-identical-source effort. The compiler/dependency recipe is only an
experiment until it matches the pinned executable; successful compilation
does not establish any behavioral or byte match.

Run `python3 generate.py`, then `python3 build_reproduce.py` for two clean
offline SBF builds and the [whole-file comparison](../../analysis/source_reconstruction/pump-fun-fees-candidate-compare.json).
Run `python3 verify_interface.py` to exercise all 31 intentionally unsupported
handlers in LiteSVM. The current candidate ELF is 289,528 bytes versus the
deployed 873,256-byte ELF; 0/31 handler bodies are behaviorally complete.
