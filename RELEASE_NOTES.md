# Runner Preflight v0.3.0 — standalone CI diagnostics preview

This is the **first versioned release from the independent public `esheenj/runner-preflight` repository**. It carries the original offline Rust CLI and the opt-in Python 3 Linux inventory collector forward from the historical v0.2.0 source snapshot, plus additional GitHub-friendly diagnostics.

## New in v0.3.0

- `inspect --input FILE --format github`: emits **GitHub Actions notice, warning, or error annotations** based on READY/WARN/HOLD findings, without echoing values, paths, tool names, labels or credentials from the supplied JSON. `--format json` continues to work exactly as before.
- Correct, integer-exact 25% free-memory and free-disk headroom thresholds (including tiny minimums and boundary cases), with independent exhaustive unit tests. Declared resource thresholds remain bounded to 1,000,000 MiB.
- Original README/onboarding, synthetic fixtures, public source-import provenance verification, locked Rust 1.100.0, and clean Linux observer remain in the independent repository.

## Downloadable assets

- `runner-preflight-linux-x86_64` — Rust CLI for Linux x86-64 (unsigned preview)
- `runner-preflight-linux-aarch64` — Rust CLI for Linux ARM64 (unsigned preview)
- `runner-preflight-source.zip` — source snapshot from the **exact published standalone repository commit**, not a rebranded parent-repo ZIP; no private history or .git directory
- `SHA256SUMS` — SHA-256 hashes for source and both binaries
- `BUILD_INFO.txt` — original source commit, GitHub Actions run and project-local Rust/Cargo toolchain evidence for each architecture

## Usage

From source (requires Rust 1.100.0/Cargo):

```sh
cd rust
cargo test --locked
cargo run --locked -- inspect --input ../fixtures/ready-x64.json --format json
cargo run --locked -- inspect --input ../fixtures/ready-x64.json --format github
```

To observe local Linux resources **only on a machine you own or administer**:

```sh
python3 scripts/collect_linux_runner.py --job fixtures/job-linux-x64.json --workspace . > observed.json
cargo run --manifest-path rust/Cargo.toml --locked -- inspect --input observed.json --format json
```

Use `job-linux-arm64.json` on ARM64. The CLI exit codes remain 0 READY, 1 WARN, 2 HOLD and 3 invalid input/usage. `WARN` and `HOLD` produce nonzero status by design.

## Exact boundaries

All conclusions are about **supplied** requirements and inventory, not authenticated host attestations, GitHub runner registration, live scheduling, configured tool versions, exchange permissions or actual production readiness. The Python observer reads only bounded local Linux resource, OS/arch and requested executable-name presence; it deliberately leaves labels and installed Rust targets unverified/empty. The browser playground remains a separate synthetic JavaScript reference, **not** Rust/WASM.

Build CI on Linux x86-64 and ARM64 verifies pinned toolchain, locked Cargo format/Clippy/tests/build, deterministic exit codes, annotations, Python observer and immutable original import provenance. The source and binaries have SHA-256 receipts; **no code signing or independent security certification** is claimed. No customer adoption, paid service, crates.io publication or live host deployment is implied. Additional recurring infrastructure spend: R0.

The historical parent-repository v0.1.0 and v0.2.0 preview releases remain published unchanged.
