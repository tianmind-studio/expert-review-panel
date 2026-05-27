## Summary

- 

## Type of change

- [ ] Eval case
- [ ] Expert library / reference material
- [ ] Output template
- [ ] Validator / test tooling
- [ ] Documentation / packaging

## Linked issue

- Related issue: 
- [ ] This PR does not use `Fixes` / `Closes` for an issue that is already completed.

## Eval-case checklist

Complete this section if the PR changes `evals/evals.json`.

- [ ] I synced with the current `main` branch before choosing the eval id.
- [ ] The eval id is the next available id and does not duplicate an existing case.
- [ ] The PR changes only the necessary eval entries and notes count.
- [ ] Existing eval assertions were not reformatted unless the PR is explicitly about formatting.
- [ ] The expected output names concrete expert roles and concrete P0/P1/P2 findings.
- [ ] Assertions are specific enough to catch weak or generic review output.

## Verification

- [ ] `python -m json.tool evals/evals.json`
- [ ] `python -m py_compile scripts/check_four_piece.py`
- [ ] `python scripts/check_four_piece.py tests/fixtures/valid-review-report.md`
- [ ] Invalid fixture still fails as expected.
- [ ] `git diff --check`

## Notes for maintainers

- Review for narrow diff first.
- For follow-up eval cases, prefer `References #...` over `Closes #...` unless the issue is specifically created for that case.
