# Seven-minute recruiter and interview walkthrough

## 1. Explain the scope

"This is a personal three-tier platform lab. I built a small operations dashboard to demonstrate application delivery, state, failure boundaries, and Azure infrastructure automation. It is not a claim of production-scale SaaS ownership."

## 2. Walk one request

Browser → Nginx → Python API → PostgreSQL. Explain that the database and API are not exposed publicly, and the frontend is localhost-only or reached through AKS port-forwarding.

## 3. Demonstrate the app

Create a task, update its status, refresh the page, and show persistence. Run scripts/smoke.py for a repeatable end-to-end check.

## 4. Show delivery

Open the PlatformOps CI workflow. Explain the difference between unit/HTTP tests with SQLite, the same contract suite against PostgreSQL, container smoke checks, manifest schema validation, and Terraform validation.

Show manual infrastructure plan/apply and the separate application release. Identify OIDC trust, source commit image tags, and rollout waits.

## 5. Demonstrate failure behavior

In a disposable Kubernetes environment, stop PostgreSQL, observe API readiness failure while liveness remains healthy, restore it, and verify stored tasks. Do not claim this demonstration was run unless it actually was.

## 6. Discuss hard decisions

- Why state is separate from application resources.
- Why readiness checks the database while liveness does not.
- Why two API replicas do not make a single-instance database highly available.
- Why tag-by-SHA is not registry immutability.
- Why this uses CI/CD rather than claiming GitOps.
- What an application rollback cannot restore.

## 7. Explain the next production step

Managed database and tested restore, auth/TLS, reviewed permissions and network access, image scanning/pinning, schema migration discipline, measured SLOs/capacity, and a reconciliation-based delivery model.

## Resume wording after verification

"Built a personal three-tier platform lab with a Python REST API, PostgreSQL, Kubernetes manifests, Terraform-defined AKS/ACR infrastructure, and GitHub Actions CI/CD; added health checks, persistent storage, network policies, and operational runbooks."

Add "deployed on Azure" only after the infrastructure and release workflows succeed and the deployment is verified. Add measured outcomes only after conducting and recording the measurements.
