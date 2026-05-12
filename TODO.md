# TODO

## Step 1 — SonarCloud CI failure

- [x] Inspect SonarCloud step in `.github/workflows/ci-pipeline.yml` and identify cause of `Unrecognized option: #`.
- [x] Fix YAML `with: args: >` block so comment lines are not passed as scanner arguments.
- [ ] Re-run CI (push/PR) to confirm Sonar-scanner succeeds.
