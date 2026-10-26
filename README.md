# Rakesh Goriga
### Platform and DevOps Engineer · Dallas, Texas

I work with Azure infrastructure, Terraform, CI/CD, and cloud operations. This portfolio documents my hands-on labs, the choices behind them, and what I learn while building and troubleshooting them.

[LinkedIn](https://www.linkedin.com/in/rakeshg1234567/) · [Portfolio](https://github.com/rockygorge/RockyProject)

## Featured project: PlatformOps Board

A three-tier operations dashboard with **Nginx + Python + PostgreSQL**, Kubernetes deployment manifests, Terraform-defined AKS/ACR infrastructure, and GitHub Actions CI/CD.

- Separate frontend, API, and persistent data tier.
- OIDC-based Azure deployment, source-SHA image tags, health checks, and rollout verification.
- Network policies, non-root application containers, resource limits, autoscaling configuration, and operational runbooks.
- **CI verified:** PostgreSQL integration, container builds, end-to-end smoke test, restart persistence, Kubernetes schemas, and Terraform validation all passed. Azure deployment remains a documented acceptance step.

**[Explore the project and run it locally](three-tier-platform/README.md)** · [Architecture](three-tier-platform/docs/architecture.md) · [Demo walkthrough](three-tier-platform/docs/demo.md) · [Verification](three-tier-platform/docs/verification.md)

## Earlier lab

### Azure platform delivery lab
A static website provisioned with Terraform and delivered through GitHub Actions using Azure OIDC federation. The lab separates state from application resources and includes validation, a saved-plan apply, publishing, and a content smoke test.

**Implemented:** Azure Storage static hosting · Terraform remote state · GitHub Actions · OIDC · RBAC · deployment concurrency · smoke testing

[Read the architecture and engineering case study](https://github.com/rockygorge/RockyProject/blob/main/docs/azure-platform-lab.md)

The source repository is currently private. The public case study describes the implementation without publishing account configuration.

## Engineering focus

- **Repeatable infrastructure:** declared configuration, remote state, and explicit provisioning boundaries.
- **Secure delivery:** short-lived deployment authentication and scoped cloud access.
- **Operability:** validation, deployment checks, troubleshooting notes, and predictable cleanup.
- **Developer experience:** setup instructions that explain both the commands and their purpose.

## Building next

I am extending my practical skills in Python automation, Kubernetes, Helm, and observability. These are learning priorities; they are not represented as completed features of the Azure lab.

## Repository guide

Original projects and case studies are linked here. Course forks elsewhere on my account are learning references and retain their original authorship.
