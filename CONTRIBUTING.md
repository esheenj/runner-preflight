# Contributing to Runner Preflight

Thanks for improving an offline-first, deterministic developer utility.

## Before opening an issue

Describe the **developer task** (which job requirement could not be evaluated), the
expected READY/WARN/HOLD result and the actual result, using *fictional* JSON.
Include the Rust version, target OS/architecture and reproduction command. Do
not paste your runner's real hostname, username, IP, environment variables,
credentials, registration tokens, workflow secrets or private repository data.
Use [the security guidance](SECURITY.md) for vulnerability reports instead.

A useful contribution includes a synthetic fixture demonstrating one problem
and a regression test explaining the expected outcome. Avoid expanding the
collector's read-only permissions, network access, shell execution or runtime
authority in ordinary feature proposals.

## Local development

On supported Linux x86-64/ARM64 machines with Rust 1.100.0 and Python 3:

```sh
cd rust
cargo fmt --all -- --check
cargo clippy --all-targets --locked -- -D warnings
cargo test --locked
cd ..
python3 -m unittest discover -s tests -v
python3 scripts/verify_import_provenance.py
```

The provenance check uses the original import commit; it needs the full public
Git history. If your checkout is shallow, fetch history through your own normal
Git client before running it. This is **not** a check against current mutable
README or CI files and does not need secrets or external account access.

Preserve schema versioning, deterministic JSON findings and exit codes
0 READY, 1 WARN, 2 HOLD and 3 invalid input. Keep bounds, no-network/no-secrets
properties, and separate user-supplied facts from verified host observations.

## Pull request expectations

Submit one small change, updated tests, a negative case and an explanation of
any user-facing contract changes. CI runs Rust unit/integration checks on x64
and ARM64, the original-import proof, and dependency advisory/license/source
audits. Package distribution, deployment and real user adoption are separate
from a successful PR. No payment, sponsorship, external account or privileged
runner registration is required to contribute.

Code and documentation in this repository are MIT licensed. Do not copy
proprietary customer/employer files or third-party code without compatible
licensing and clear attribution.
