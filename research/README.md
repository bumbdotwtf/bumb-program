# Integrated Pump.fun research

`imported-lab/` is a byte-preserved, selected import from
`NubsCarson/solana-program-research-lab` at commit
`13a7f937ace1041d5d3116472335b6c20bedf5e1`.
`import-manifest.json` records all 62 original file hashes, sizes and the selection
rule. The source repository was private at import time. The user explicitly authorized
public publication of the imported Pump.fun material in this chat.

Imported work includes all of that commit's `analysis/pump_fun`,
`inputs/pump_fun`, `scripts/pump_fun*`, Pump.fun source-reconstruction reports and
`reconstruction/pump-fun-fees-candidate`, plus transitive Python helpers and
Surfpool download provenance. The three original program payloads match this
project's corresponding captures byte for byte. This import adds no Mayhem source.
The lab's separately named daos.fun `pump_xyk`, `pump-full-candidate` and
`pump-migrate-v2` target a different program and are deliberately excluded.

The snapshot is immutable. Run its scripts in a disposable working copy using the
root integration runner; do not overwrite original receipts with new runs.
The runner verifies import hashes, compares all three original binaries, initializes
the exact official-docs Git checkout from a supplied local clone, and executes the
saved-receipt verifiers. It can additionally run the four signed offline Surfpool
sequences and verify their freshly generated receipts. It does not call public RPC.

```sh
python3 scripts/verify_imported_lab.py --docs-checkout /path/to/pump-public-docs \
  --output work/lab-check
python3 scripts/verify_imported_lab.py --docs-checkout /path/to/pump-public-docs \
  --output work/lab-runtime-check --surfpool /path/to/surfpool-1.6.1
```

Use the Python environment from the root `requirements.txt`. The documented
upstream environment used solders 0.29.0; the integration checks here use the root's
0.27.1. Surfpool must be 1.6.1; its upstream archive URL and digest are retained in
`imported-lab/evidence/tool-downloads.json`. The older installed Surfpool 1.0.0
was not used. Every runtime run starts a fresh offline in-memory loopback instance.

## What the imported work establishes

- 125 published selectors map to direct dispatcher wrappers in the same three
  program captures already used by this project.
- Saved receipts have verifiable signatures, binary/fixture hashes, rollback
  checks and bounded state/balance assertions. Fresh replays are recorded separately
  under `validation/`; saved receipts alone are not fresh execution evidence.
- The recovered experimental Fees selector in the main `programs/` tree remains
  independent of the imported 31-handler Anchor scaffold. Every scaffold handler
  intentionally returns unsupported, so it cannot replace any deployed program.
- The scaffold's source matches its imported build manifest. The reported two
  matching scaffold builds are historical upstream evidence. Its generated ELF
  was not checked into the source repository and has not been rebuilt here. Do not
  count that reported hash as a new locally verified build or a deployed match.

## Local integration validation

All seven saved-receipt verification scripts pass. All four fresh offline runtime
sequences pass, followed by all seven verifiers on the fresh receipts. The run
contains 30 unique signed transaction payloads across configuration guards,
creation/trades, completion/migration, post-migration trades and fee withdrawal.
`validation/fresh-runtime-verification.json` records the tool hash and each step;
`validation/fresh-receipt-manifest.json` pins all eight fresh receipt files.
The source snapshot remains unchanged and every original import hash still matches.

## Using this for continued reconstruction

Use the imported state fixtures and signed lifecycle harness as the baseline for
original-versus-rebuilt differential tests. Preserve the exact original program
hashes and dependency qualifications. Replace scaffold handlers only as actual
constraints, account layouts, state changes, arithmetic and error precedence are
recovered. Use the root byte comparator for complete allocation comparisons and
retain source/build provenance. Full byte-identical programs and the consolidated
security audit remain the completion requirements.

Historical Markdown links to unrelated daos.fun controls or upstream submodules
are retained verbatim for provenance; the root integration runner supplies the
needed official-docs checkout. Unrelated lab protocols are not imported or audited.
