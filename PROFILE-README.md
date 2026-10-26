# Rakesh Goriga
### Platform and DevOps Engineer · Dallas, Texas

I work with Azure infrastructure, Terraform, CI/CD, and cloud operations. This portfolio documents my hands-on labs, the choices behind them, and what I learn while building and troubleshooting them.

[LinkedIn](https://www.linkedin.com/in/rakeshg1234567/) · [Portfolio](https://github.com/rockygorge/RockyProject)

## Featured build: PlatformOps Board

A three-tier web application with a Python API and PostgreSQL, Kubernetes manifests, Terraform-defined AKS/ACR, and GitHub Actions delivery. Includes health checks, persistent storage, network policies, contract tests, and operations documentation.

[Explore the code and demo walkthrough](https://github.com/rockygorge/RockyProject/tree/main/three-tier-platform) · [Verification status](https://github.com/rockygorge/RockyProject/blob/main/three-tier-platform/docs/verification.md)

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
