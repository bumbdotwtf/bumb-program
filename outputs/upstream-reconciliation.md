# Upstream reconciliation, 25 October 2026

The verified checkpoint `b3f23323` is reconciled with upstream `bde19c4e`. All 266 incoming paths are accounted for in `resolution.json`. Incoming research, receipts and candidate artifacts are retained. Upstream versions of protected active files are copied byte-for-byte into `upstream-files/`; their accepted counterparts are in `accepted-files/`.

The merge had three text conflicts: the workflow, Pump README and status registry. Git also automatically merged other active files. Those automatic merges were reviewed explicitly: they would enable excluded Pump handlers, replace newer accepted candidates and weaken the current source-binding verification. The full accepted Pump tree, workflow, status, source/build verifiers and audit/recovery documentation therefore remain unchanged. Incoming alternatives remain available for later permitted review.

No stopped handler, synthetic Mayhem caller, source-path remap, alternative compiler recipe or new runtime probe was executed. Existing upstream claims of additional recovered handlers, test counts or compiler success are not adopted as accepted results here. The v1.43 package is preserved as an unverified alternative; the verified v1.44 build recipes remain active.

Current acceptance remains 140/150 bounded implemented handlers, five partial and five unrecovered; exact whole-file identity remains 0/4 core programs and 2/5 dependency capture comparisons. These measures do not imply an overall completion percentage. The next three isolated Pump, AMM and Fees corrections continue from the same verified inputs.

Run `python3 -B verify.py` for frozen evidence integrity, or add `--current /path/to/repo` to check the resolved checkout. The verifier does not import or execute incoming research code.

Published work remains on `codex/layered-reconstruction`; the reconciliation preserves the upstream history and records explicit active-file resolutions.
