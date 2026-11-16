# Runner Preflight v0.4.0 — offline Actions job-stage evidence

Runner Preflight is an original MIT-licensed, offline Rust CLI for checking
declared CI runner inventories against job requirements. This standalone Linux
x64/ARM64 preview retains all v0.3.0 `inspect` behavior and adds an independently
tested, narrower job-stage diagnostic.

## New in v0.4.0

- `actions-job --input FILE --format json`: classify a **supplied** GitHub Actions
  job JSON record as `FAILED_WITHOUT_RECORDED_STEPS`, `FAILED_WITH_RECORDED_STEPS`,
  `NOT_TERMINAL`, `GITHUB_REPORTED_SUCCESS` or inconclusive terminal state.
- A job with no steps and `runner_id: 0` is **not** proof of a particular billing,
  GitHub-hosted allocation, repo Actions setting or workflow-source failure.
  Output explicitly sets `root_cause_verified:false` and directs maintainers to
  GitHub check-run annotations / Actions settings, without claiming access.
- Input is a bounded regular file (max 64 KiB, no symlinks); the diagnostic never
  reproduces user-controlled runner labels, job names, paths, URLs, IDs, step
  contents, tokens or logs. Only fixed codes and messages leave the tool.
- Synthetic no-step and executed-failure fixtures, negative tests and both
  architecture smoke checks cover the new functionality.
- Existing `inspect --input FILE --format json|github` and exit codes
  0 READY, 1 WARN, 2 HOLD, 3 invalid input remain unchanged.

## Reproduce the new CLI behavior

From the source ZIP root (Rust 1.100.0 and Cargo required):

```sh
cargo run --manifest-path rust/Cargo.toml --locked -- actions-job --input fixtures/actions-job-prestep.json --format json
# HOLD: FAILED_WITHOUT_RECORDED_STEPS (exit 2)

cargo run --manifest-path rust/Cargo.toml --locked -- actions-job --input fixtures/actions-job-step-failure.json --format json
# HOLD: FAILED_WITH_RECORDED_STEPS (exit 2)

cargo run --manifest-path rust/Cargo.toml --locked -- inspect --input fixtures/ready-x64.json --format json
# READY (exit 0)
```

The tool reads no GitHub token, never calls the GitHub API and makes no claim
that a runner is registered or a private-job failure has been repaired.
Users should sanitize saved real job JSON before sharing it anywhere.

## Distributed assets and verification

- `runner-preflight-linux-x86_64`: unsigned Linux x64 native Rust CLI.
- `runner-preflight-linux-aarch64`: unsigned Linux ARM64 native Rust CLI.
- `runner-preflight-source.zip`: original public standalone repository snapshot
  at the exact release commit; no `.git` history and no private control source.
- `SHA256SUMS`: hashes of both binaries and source snapshot.
- `BUILD_INFO.txt`: commit and per-architecture toolchain receipts.

Protected GitHub Actions release workflow publishes only after exact-main
qualification, Rust 1.100.0 fmt/Clippy/tests/build, negative/synthetic CLI
checks, Python Linux observer tests, original import provenance, dependency
advisory/license/source audit, same-run architecture artifact checks and
release hash verification. Existing `v0.3.0` and older parent-repository
releases are retained without moving tags.

**Limitations:** Linux only for built binaries and opt-in local observation;
unsigned preview; not a hosted CI runner, scheduler, account-billing diagnostic,
attested host, commercial support contract, signing authority or production
access. No real-world usage, revenue or customer adoption is inferred from
publication. Additional recurring infrastructure spend: R0.
