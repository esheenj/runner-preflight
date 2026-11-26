# Preserve CI preflight evidence

Store preflight output alongside the commit SHA, job specification and supplied inventory used for the run. Record a SHA-256 digest for each input and the output so a reviewer can match the report to the files they receive.

Before reusing a report, check the commit and input digests against the job you are evaluating. Rerun preflight if any input changed. A matching digest establishes file consistency. Use a trusted CI artifact or a separately authenticated receipt when provenance matters.

For example, a fictional job can require an ARM64 runner while the supplied inventory describes an x86-64 runner. Keep that report with the inventory that produced it. After replacing the inventory with an ARM64 one, generate a new report for the updated input.
