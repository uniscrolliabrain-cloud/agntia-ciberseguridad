# Offline supply-chain fixtures

Tests generate `requirements.txt` for `agntia-demo-package==1.0.0` (affected) and `==2.0.0` (synthetic fixed version). A deterministic OSV-schema advisory `AGNTIA-TEST-0001` lives in a tiny offline PyPI DB ZIP. The package is fictional; nothing is installed and no external database/API is queried during scans. This checks the real OSV executable and offline matching, not production vulnerability coverage or DB completeness.

Additional cases: no ecosystem cache, stale metadata, malformed JSON, unpinned package version and source-provided ignore policy. Missing observations are exported as `not_observed`, never automatically resolved/fixed. Licenses and direct/transitive relationships remain `unknown` if absent from evidence.
