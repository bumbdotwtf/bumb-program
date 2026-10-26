# Third-party source notice

The complete vendored solana-pubkey 2.4.0 source originates from the published crate archive with SHA-256 `9b62adb9c3261a052ca1f999398c388f1daf558a1b492f60a6d9e64857db4ff1`. Its manifest declares Apache-2.0; the archive contains no LICENSE or NOTICE file. The upstream LICENSE at the archive-recorded Git commit is supplied alongside this notice.

Modified files: `src/lib.rs` restores the retained stack-buffer bs58 formatter and checked UTF8 conversion; `Cargo.toml` adds the already-locked bs58 0.5.1 dependency with default features disabled. All other archive member bytes remain unchanged. The full modification patch and original archive are retained as evidence. These notices are outside the frozen compiled input tree.
