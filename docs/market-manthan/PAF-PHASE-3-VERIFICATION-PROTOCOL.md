# PAF Phase 3 Native CI Verification Protocol

The verification gap is addressed without depending on the repository's blocked third-party Action allowlist.

## Method
- GitHub-hosted native runner.
- Shell commands only.
- Repository source cloned directly.
- Python standard library loads the Phase 3 test module.
- Every `test_*` function is executed explicitly.
- Any assertion or import failure causes a non-zero workflow exit.

## Evidence rule
Only a completed successful workflow run for `market-manthan-paf-verification.yml` may be used to promote the Phase 3 receipt from VERIFICATION IN PROGRESS to VERIFIED.

No green run means no VERIFIED claim.
