# Verification record

## Executed in the authoring environment

- Six standard-library unittest test cases passed against the SQLite adapter.
- Tests exercise the HTTP API create/update path and persisted data, invalid input, SQL payload handling, missing routes, database-outage readiness behavior, and metrics accounting.

## Configured for GitHub Actions

- Repeat the contract tests against a disposable PostgreSQL 16 service.
- Build both container images and start the three-tier Compose stack.
- Smoke test Nginx → API → PostgreSQL.
- Restart the API and check that a previously created task persists.
- Validate Kubernetes objects with kubeconform.
- Initialize the Terraform provider without a backend and run terraform validate.

CI execution results must be checked on GitHub; configuration alone is not proof that these checks passed.

## Not yet verified

Docker, kubectl, Terraform, and an Azure session were not available in the authoring environment. No Azure resources were provisioned. Kubernetes scheduling, NetworkPolicy enforcement, CSI persistence, HPA behavior, Azure identity/RBAC, and the application release remain deployment acceptance checks.

## Acceptance checklist

- [ ] All PlatformOps CI jobs pass on the published commit.
- [ ] Azure plan reviewed and cloud cost accepted.
- [ ] Infrastructure apply succeeds.
- [ ] Release builds/pushes images and all Kubernetes rollouts succeed.
- [ ] Full smoke test passes through the web service.
- [ ] Database outage/recovery and task persistence tested.
- [ ] Rollback of a known compatible app revision tested.
- [ ] Cleanup behavior and remaining resources reviewed.
