# Security and data boundaries

Runner Preflight evaluates **supplied** runner/job data. The optional Linux
collector is read-only and opt-in, and is not a CI runner administrator,
credential holder, remote shell, network scanner or security attestation tool.

## Reporting issues

For a suspected vulnerability, use GitHub's **private vulnerability reporting**
option in this repository's **Security** tab **if that feature is enabled**.
If the feature is unavailable, do not publish exploit details, credentials or
host-identifying data in a public issue. Contact a maintainer through an
already-established private channel if one is available; no response time or
private intake address is guaranteed. Ordinary non-sensitive bugs can use
GitHub Issues with entirely synthetic input.

Never include live CI registration tokens, GitHub Actions secrets, personal
details, IP addresses, environment variables, raw host inventories or private
repository excerpts in a report.

## Supported scope

- Source CI: Linux x86-64 and ARM64 (Rust 1.100.0; Python 3 standard-library
  observation on Linux). Windows and macOS inputs may be evaluated as **supplied
  data**, but no automatic observation or release-platform support is claimed.
- Source security CI checks locked Rust dependencies and advisories using a
  pinned auditing action; a green job is not proof that no vulnerability exists.
- No host or exchange actions are authorized. `READY` validates only a supplied
  machine inventory against a supplied job contract.
- Dependency or schema security issues should produce a synthetic regression
  case and remain a separate, explicitly qualified release decision.
