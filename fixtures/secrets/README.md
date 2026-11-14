# Secret fixtures

Only a non-functional canary matching `AGNTIA_TEST_SECRET_[A-Z0-9]{32}` is generated at test time. It is never an API token. Expected true positive: the canary rule. False positive/control: an ordinary public identifier. A binary fixture verifies explicit acquisition metadata; binary-language detection coverage is not claimed. The real contract test checks the minimized export for the canary value and ignores source-provided allow comments/config.

No credential is tested against a real provider. The recommendation is a reviewed rotation proposal.
