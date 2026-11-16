# Runner Preflight

Offline, read-only CI runner requirement matching with deterministic JSON reports.

Runner Preflight evaluates a **supplied** inventory against a declared job specification. It **does not** inspect a host automatically, register CI runners, diagnose GitHub scheduling or billing, install software, access credentials, or repair a server. It does not grant financial or agent execution authority.

## Latest standalone download — v0.3.0

**[Runner Preflight v0.3.0 (Linux preview)](https://github.com/esheenj/runner-preflight/releases/tag/v0.3.0)** is published from this independent repository. Download the [x86-64 binary](https://github.com/esheenj/runner-preflight/releases/download/v0.3.0/runner-preflight-linux-x86_64), [ARM64 binary](https://github.com/esheenj/runner-preflight/releases/download/v0.3.0/runner-preflight-linux-aarch64), [complete source ZIP](https://github.com/esheenj/runner-preflight/releases/download/v0.3.0/runner-preflight-source.zip), or [SHA-256 manifest](https://github.com/esheenj/runner-preflight/releases/download/v0.3.0/SHA256SUMS).

The [exact-main release CI](https://github.com/esheenj/runner-preflight/actions/runs/43838965049) passed both Rust 1.100.0 Linux builds, synthetic READY/WARN/HOLD and `--format github` smoke tests, Linux observer integration, source packaging and hash checks. The immutable release tag points at `1ecffdf095826e2b05d831cecce67c43bbdd385c`. These are **unsigned preview binaries**; neither code signing, production runner enrollment nor commercial support is claimed. Existing historical [v0.2.0 upstream downloads](https://github.com/esheenj/compound-intelligence-starter/releases/tag/runner-preflight-v0.2.0) remain available.

## Try it in a minute

For developers who want to know whether a **declared CI job** matches a runner inventory before assigning it, clone this standalone repository on Linux x86-64 or ARM64 with Rust 1.100.0 and Cargo:

```sh
git clone https://github.com/esheenj/runner-preflight.git
cd runner-preflight
cargo run --manifest-path rust/Cargo.toml --locked -- inspect --input fixtures/ready-x64.json --format json
```

Expected JSON contains `"status":"READY"`. To see how a missing requirement produces an actionable result, run `cargo run --manifest-path rust/Cargo.toml --locked -- inspect --input fixtures/hold-arch.json --format json`; this exits with code 2 (`HOLD`) rather than silently approving the job. The [original offline playground](https://esheenj.github.io/compound-intelligence-starter/runner-preflight.html) lets developers try the same synthetic contract without installing Rust; it is a JavaScript reference, not a host inspector.

### GitHub Actions-friendly output

Use `--format github` instead of `--format json` to emit GitHub Actions workflow annotations directly: `READY` is a **notice**, low resource headroom is a **warning**, and a missing requirement is an **error**. This follows [GitHub's workflow command convention](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands). It uses **static reason codes and messages only**; user-provided runner labels, paths, usernames, job values, host identifiers and credentials are never copied to workflow annotations. Output stays offline.

```sh
cargo run --manifest-path rust/Cargo.toml --locked -- inspect --input fixtures/ready-x64.json --format github
# ::notice title=Runner Preflight::READY - Declared requirements match; no host attestation.
```

When used as a step in your own GitHub Actions workflow, `WARN` exits **1** and `HOLD` exits **2**, so both require explicit handling if you wish the step to continue. The conventional JSON format, schema and exit codes remain unchanged. A preflight outcome **only evaluates supplied claims**: it does not prove a runner is registered, online or scheduled. Disk and memory headroom warns when observed free resources are strictly less than 125% of the declared minimum, including small integer values with no spare capacity.

To validate source and its Rust dependencies:

```sh
cd rust
cargo fmt --all -- --check
cargo clippy --all-targets --locked -- -D warnings
cargo test --locked
```

The tool cannot register runners, attest a host, access your GitHub account, fix billing or resolve job scheduling by itself. `READY` means only that **the supplied facts** meet the supplied requirements.

## Offline GitHub Actions job-stage triage (source-only candidate)

GitHub may mark a job **failed before any runner or execution steps are recorded**.
This is different evidence from a failing test. The new **`actions-job`** subcommand
accepts a bounded, locally supplied GitHub REST `/actions/jobs/{id}` JSON
record and classifies the recorded stage **without making any network or
credential calls**. It deliberately does not determine why GitHub did not
allocate the runner or quote user-controlled workflow metadata.

```sh
cargo run --manifest-path rust/Cargo.toml --locked -- \
  actions-job --input fixtures/actions-job-prestep.json --format json
# "status":"HOLD","signal":"FAILED_WITHOUT_RECORDED_STEPS" (exit 2)
cargo run --manifest-path rust/Cargo.toml --locked -- \
  actions-job --input fixtures/actions-job-step-failure.json --format json
# "status":"HOLD","signal":"FAILED_WITH_RECORDED_STEPS" (exit 2)
```

For a failed job with no recorded steps, inspect **GitHub check-run annotations**
and account/repository Actions runner policy or billing separately. Without
those records, the tool sets `root_cause_verified:false` and does not claim
quota exhaustion, bad source tests or a broken self-hosted runner. Queued
jobs are `NOT_TERMINAL` (exit 1); GitHub-reported successful jobs are
`GITHUB_REPORTED_SUCCESS` (exit 0), not independent production attestation.

The input limit is 64 KiB, regular file only, no symlinks; unexpected job
metadata is ignored and never echoed. Do not save or publish private job JSON
containing actual credentials. The synthetic fixture data above includes
no real private workflow content. This functionality is **newer than the
published v0.3.0 binaries** and requires building the current source. It
will not be advertised as a shipped release feature until a separately
verified versioned distribution exists.

## Optional: observe your own Linux runner

The accompanying **Python 3 standard-library** observer reads a deliberately small set of current host facts locally, then generates input for the Rust evaluator. This is a complementary Python/Rust workflow, not a replacement for the Rust engine and **not present in the original v0.1.0 release**.

Run these commands from the extracted standalone source root on your **own authorized Linux x86-64 machine** (choose `job-linux-arm64.json` on ARM64):

```sh
python3 scripts/collect_linux_runner.py --job fixtures/job-linux-x64.json --workspace . > observed.json
cd rust
cargo run --locked -- inspect --input ../observed.json --format json
```

The observer takes a job-only `runner-preflight-job-v1` JSON file and records Linux OS/architecture, free disk for the **specified workspace filesystem**, `/proc/meminfo` `MemAvailable` and presence of only the **requested executable names** on PATH. It reads files and metadata only: **no network, credentials, SSH, privileged commands, installs, subprocesses or filesystem mutations**. It writes its manifest to stdout, so redirect it to a local file only if you want to keep it.

The result is **not attested**. A tool name being present does not prove its version or functional readiness; OS resource values are point-in-time estimates in MiB and capped at the CLI's 1,000,000-unit input bound. Labels and installed Rust targets are intentionally left empty because they cannot be independently verified through this small observer. Jobs requiring those claims receive HOLD unless separately verified and supplied using another provenance-aware workflow. No output includes IP addresses, usernames, hostnames, environment variables, executable paths or secrets.

An invalid or symlinked job input (64 KiB maximum), unsupported host or unavailable Linux observation exits 3. The collector is intentionally Linux-only and never repairs CI runner registrations, scheduling, billing, disk capacity or software.

## Contract

The input JSON (maximum 64 KiB, regular file only, no symlinks) has `schema: "runner-preflight-input-v1"`, plus:

- `runner`: `os`, `arch`, `labels`, `disk_free_mb`, `memory_free_mb`, `tools`, and `rust_targets`
- `job`: `os`, `arch`, `required_labels`, `min_disk_mb`, `min_memory_mb`, `required_tools`, and optional `rust_target`

`os` is `linux`, `macos`, or `windows`. `arch` is `x86_64` or `aarch64`. Tool and target comparisons match exact identifiers; they do not discover installed versions. The output uses `runner-preflight-result-v1`, a status and generic machine-readable findings.

| Exit code | Meaning |
|---|---|
| 0 | READY: declared requirements matched |
| 1 | WARN: requirements matched but disk or memory has **less than 25% spare capacity** above the declared minimum |
| 2 | HOLD: one or more requirements missing |
| 3 | Invalid input or CLI usage |

## Independent source and verification

The [standalone v0.2.0 import](https://github.com/esheenj/runner-preflight/commit/ea0c21d1a5da31fb59cafb31324f413256309739) originated from explicitly allowlisted, original, **public** files in [Compound Intelligence Starter](https://github.com/esheenj/compound-intelligence-starter/tree/main/experiments/runner_preflight). `SOURCE_PROVENANCE.json` describes that **immutable import snapshot**, not every future commit in this evolving repository. `scripts/verify_import_provenance.py` independently checks the original Git blobs, hashes and sizes in CI; normal README and workflow improvements do not rewrite the import evidence.

The [independent repository CI](https://github.com/esheenj/runner-preflight/actions) tests Linux x86-64 and ARM64 Rust qualification, local observer compatibility, original import provenance, and dependency advisories/licenses/sources. Each source revision needs its own passing CI before release. **[Standalone versioned downloads](https://github.com/esheenj/runner-preflight/releases)** are published only after a successful exact-main CI run and immutable-tag checks; their presence and checksums must be verified on the Releases page rather than assumed from source commits. The historical [v0.2.0 preview binaries](https://github.com/esheenj/compound-intelligence-starter/releases/tag/runner-preflight-v0.2.0) remain available in the upstream research repository.

MIT licensed (see `LICENSE`). Read [contribution guidelines](CONTRIBUTING.md) and [security reporting guidance](SECURITY.md) before sharing a bug report. Do not advertise an executable as signed, certified, actually inspecting an Oracle host, or commercially supported merely because source tests pass. No additional recurring infrastructure spend or paid dependency is required.

### Resource thresholds

The job's `min_disk_mb` and `min_memory_mb` are minimum requirements. Below either minimum means `HOLD`. Meeting a **positive** minimum with less than 25% additional capacity means `WARN`, including the small case of 1 MiB available against a 1 MiB requirement; exactly 25% headroom or more is `READY` when other checks pass. A zero minimum does not trigger a headroom warning. These are calculations on supplied/observed estimates, not a guarantee that a CI job will start.
