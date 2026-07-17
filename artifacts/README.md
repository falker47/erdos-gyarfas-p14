# Generated research artifacts

This tree holds machine-readable evidence produced by actual runs. No file in
the bootstrap scaffold is a mathematical certificate.

- `manifests/`: run truth, including failed, refused, and interrupted runs.
- `certificates/`: certificate artifacts after a format and verifier are
  accepted. The current schema is provisional and non-certifying.
- `counterexamples/`: canonical graph candidates and independent verifier
  reports.
- `checkpoints/`: resumable state tied to an exact program and manifest.

Material artifacts must use repository-relative paths, deterministic JSON
serialization where applicable, SHA-256 hashes, and the schemas documented in
`docs/ARTIFACT_FORMATS.md`. Large artifacts may be retained by CI rather than
Git, but their manifests and hashes remain required.

A filename, exit code, empty log, or schema-valid JSON object is not evidence
of exhaustive coverage. Acceptance of a mathematical conclusion is governed
by `research/VERIFICATION_PROTOCOL.md`.
