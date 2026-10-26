# SDK sweep and creator-update object coverage

The [authenticated source expansion](../repro/sdk/sweep-setcreator-source-20261026/REPORT.md) binds eight more of the original dynamic account-object sites: four AMM fee sweeps supply all 12 IDL fields, two Pump curve sweeps supply nine of 13, and two conditional AMM creator-update sites supply one or three of five. The exact earlier eight site IDs and new eight are disjoint; nine of the original 25 remain unexpanded. This counts symbolic object bindings within the existing builder inventory, not instructions or runtime compatibility.

The [independent source and portability review](../repro/sdk/sweep-setcreator-source-independent-review-20261026/REPORT.md) confirms helper argument substitutions, complete object expressions, IDL ordering/flags/omissions and the conditional creator branches. Fresh relocation passed with exact-case paths and no stale workspace reads. Source seal: `ee143e26fcf33efee56fb421e6a2e604baa029ae4e51b07c7b170d1c74f19052`. Review seal: `d3a2cddb74cb5d1d3a2a86c77fe175e1a6d093d367b737486f992bdccc847e9c`.

Pump curve sweeps leave global, associatedTokenProgram, systemProgram and bondingCurve to resolution; their IDL recipes are retained. Creator updates without baseMint leave mint-derived accounts dependent on pool data. The online wrapper reads/decodes the pool, prepends extension below 300 bytes, then supplies baseMint explicitly. Client decoding padding and account extension are separate steps. The omitted program field has no IDL address/PDA recipe in the source packet. The subsequent compiled-wrapper observation below measures the supplied-baseMint branch and retains both omitted-baseMint failures.

The source packet itself ran no SDK JavaScript or Anchor method. Its static findings remain distinct from the later runtime experiment.

## Actual compiled-wrapper observation

The [saved runtime audit](../repro/sdk/sweep-setcreator-runtime-20261026/REPORT.md) binds one actual offline run of the public compiled SDK exports. Four AMM sweeps, two Pump curve sweeps and two creator updates with supplied baseMint constructed eight instructions; their program IDs, discriminators and all 84 ordered account metas match independent expectations. Numeric PDA/ATA checks cover sixteen derivation records and thirteen unique addresses. Both calls that omitted baseMint failed with unresolved metadata and bondingCurve accounts; they are preserved as resolver errors, not successful construction.

All 4,749 graph files remained unchanged. The observer recorded 316 loaded modules and one genuine bufferutil native addon load. Thirteen missing bigint native resolution candidates produced the recorded pure-JavaScript fallback; they were not native dlopen failures. No guarded RPC, transport or signing calls were observed. This is a Node-level observation, not an operating-system isolation claim.

Runtime review seal: `cec59238fb6f08abd74358642b771544da59d9e6e2a393220bec4e5d552c2ebb`. The [separate relocation receipts](../repro/sdk/sweep-setcreator-runtime-portability-20261026/observation.json) retain zero exact-case/workspace violations, seal `ce92f8b75de5612069178f9ab1398c0e2ed43e902a4e8968cb151f16a8277535`. Replay only saved data with:

```sh
python3 -B repro/sdk/sweep-setcreator-runtime-20261026/verify.py --expected-seal cec59238fb6f08abd74358642b771544da59d9e6e2a393220bec4e5d552c2ebb
```

The portable checker executes standard-library Python on bundled observations and reads compiled JavaScript as inert evidence. It does not rerun SDKs, import native crypto utilities, sign transactions or contact RPC. The synthetic client inputs do not establish valid real pool/mint/token/metadata state, recipient membership, account extension, target execution or arbitrary resolver compatibility. Nine dynamic object sites remain unexpanded. Source/compiler/dependency identity and whole-byte identity remain open; core whole-file identity is still 0/4. Active program source, selected artifacts, status, workflows and historical packets are unchanged.
