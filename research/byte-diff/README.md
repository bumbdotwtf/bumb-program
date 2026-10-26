# Locate differences in unmodified compiler output

`research/byte-diff/byte_diff.py` compares two files exactly as supplied and records contiguous
mismatch ranges. It accepts explicit paths, so it works with both the four core
captures and the five dependency captures. It uses only the Python standard
library and the existing `compare()` helper.

```sh
python3 -B research/byte-diff/byte_diff.py \
  evidence/original/pump/deployed.so /path/to/independently-built/pump.so \
  --output work/pump-raw-diff.json
```

Exit codes:

- **0:** every input byte and the complete lengths match.
- **1:** at least one changed, missing or extra byte.
- **2:** invalid arguments or a file error, including an existing output file.

The tool never pads, trims, aligns, normalizes or rewrites either input. A missing
zero allocation suffix is still a difference and returns 1. The report binds both
input files by SHA-256 and records `source_provenance_verified: false`. Supplying
the captured original twice would demonstrate file equality only, not a source
reconstruction. Source, compiler and build provenance need separate verification.
This is a file comparator: it does not validate ELF structure or execute a program.

## Reading the report

Each range uses positional file offsets `[start, end)`, with an exclusive `end`:

- `changed`: both files contain bytes at these offsets, and every paired byte differs.
- `candidate_missing`: the candidate ends before this portion of the original.
- `candidate_extra`: these candidate bytes extend beyond the original.

Adjacent changed bytes form one range. Length-only tails are separate, even when
adjacent to a changed range. Each side includes at most 16 bytes of hex preview;
`length` always covers the complete range. The default limit is 1,000 ranges.
`--max-ranges 0` retains totals only. Counts and the exit code always cover both
complete files; `ranges_omitted` explicitly records any omitted ranges.

`different_positions_in_shared_length` counts changed paired bytes.
`differing_or_missing_original_positions` adds original bytes missing from the
candidate. `total_differing_positions` also counts candidate bytes beyond the
original. These are positional diagnostics, not semantic distance, aligned
function differences or source-completion percentages. An insertion can shift
later bytes and produce many positional mismatches.

The historical `scripts/compare.py` and its allocation-image option remain
unchanged because existing evidence packages bind that helper. This command adds
an explicitly raw comparison entry point and range localization; it does not
promote any artifact or change accepted reconstruction counts. The new files stay
under `research/byte-diff/` because the current P27 guard binds the exact inventory
of 187 top-level Python scripts and six workflows. No existing guard or manifest
is relaxed to introduce this tool.

## Regression checks

```sh
python3 -B research/byte-diff/test_byte_diff.py
python3 -B scripts/test_tooling.py
```

The tests cover missing zero tails, extra bytes, disjoint changes, bounded range
and hex output, CLI exit codes, input/report preservation and all 225 pairs of
binary strings up to three bytes against an independent positional oracle.

The CLI was also checked against these existing saved artifacts; this is a replay
of comparisons, not a fresh compiler run:

| Capture | Candidate under `repro/pump/` | Observed raw comparison | Exit |
| --- | --- | --- | --- |
| `associated_token` | `ata-candidate-build-2/spl_associated_token_account.so` | 307 changed bytes in 126 ranges; no length difference | 1 |
| `spl_token` | `verified-spl-token/pinocchio_token_program.so` | Complete byte equality; no ranges | 0 |
| `spl_token_2022` | `verified-token-2022/spl_token_2022.so` | Shared bytes equal; 770,960 captured bytes missing in one tail | 1 |

For example, reproduce the ATA comparison from the repository root:

```sh
python3 -B research/byte-diff/byte_diff.py \
  evidence/dependencies/associated_token/deployed.so \
  repro/pump/ata-candidate-build-2/spl_associated_token_account.so \
  --output work/ata-raw-diff.json
# Expected exit: 1. The candidate's original 307-byte gap remains unresolved.
```
