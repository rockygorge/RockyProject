# Architecture and engineering decisions

## Request and data flow

The browser loads static assets from Nginx. Nginx proxies /api/ requests to the Python service on the cluster network. The API validates input and executes parameterized SQL against PostgreSQL. No database port or API port is published on the host in Compose; only the frontend is bound to 127.0.0.1.

In Kubernetes all application services remain internal. Users authenticate to AKS and use kubectl port-forward to reach the frontend. This avoids presenting an unauthenticated application as a public production service.

## Control plane and delivery

Terraform owns the Azure resource group, AKS, ACR, Log Analytics workspace, and deployment role assignments. Kubernetes manifests own the application objects. The database Secret is created at deployment time from a GitHub environment secret.

GitHub Actions uses OIDC federation with Entra. Infrastructure state remains in a separately bootstrapped account and a dedicated platformops-dev.tfstate key. Applying this stack does not overwrite the earlier static website lab state.

Application images are tagged with the full source commit SHA. A release renders image references into temporary manifests before applying them, waits for PostgreSQL and API readiness, then rolls out Nginx and runs a full HTTP smoke test.

This is push-based CI/CD. It is not GitOps reconciliation. Argo CD is a future extension.

## Decisions and tradeoffs

| Decision | Reason | Limit |
| --- | --- | --- |
| Separate web, API, and data tiers | Independent scaling and distinct failure boundaries | More moving parts than a single process |
| Same-origin reverse proxy | No browser-visible backend address or permissive CORS required | Nginx needs API service DNS at startup |
| Two API/web replicas | Demonstrate rolling deployment and availability patterns | Database is a single point of failure |
| Separate liveness/readiness | A DB outage should remove API readiness without restart storms | Readiness probes add DB queries |
| PostgreSQL StatefulSet and PVC | Demonstrate persistent state, pod replacement, and storage ownership | No HA, backups, PITR, or production data guarantee |
| API HPA | Demonstrate CPU-based horizontal scaling | Needs metrics-server; not a measured capacity model |
| API disruption budget | Preserve one replica during voluntary eviction where possible | Does not prevent crashes, node failure, or all deployment disruption |
| Default-deny network policy | Express web → API → DB boundaries | Requires an enforcing network plugin; verify in a real cluster |
| No public ingress | Safe review without application auth | Not an internet-facing portfolio deployment |
| Standard-library Python HTTP layer | Small dependency surface and executable tests without framework setup | Bounded demo, not a production-grade app server |
| Per-request DB connections | Clear transaction boundary and no global shared connection | Pooling and connection limits needed before scaling |
| Startup schema bootstrap | Keep the demo easy to run | Replace with versioned migration jobs for production |

## Security model

- AKS local accounts disabled; Entra/Azure RBAC is used for administrative access.
- ACR admin credentials disabled; kubelet gets AcrPull, deployer gets AcrPush.
- GitHub federation is bound to repository and the platformops-dev environment.
- App containers run non-root with read-only roots, no privilege escalation, and dropped capabilities.
- Pod service-account tokens are not mounted.
- PostgreSQL password is supplied at deployment, never committed.
- Web input is displayed through textContent, not inserted as HTML.
- SQL parameters are bound through the database driver.
- Request bodies have size limits; client-visible errors omit backend details.
- Kubernetes Secrets are base64 encoded, not a substitute for an external secrets manager.
- Database traffic is isolated by policy but not application-layer TLS in this lab.
- CI/schema dependencies are tag-versioned, not fully digest/SHA pinned.

## Observability

The API exposes /healthz, /readyz, and /metrics. Metrics include request count, server-error count, and request duration sum/count. They include probes and are demonstrations rather than an SLO dashboard. The manifests add scrape annotations, but do not deploy Prometheus or automatically grant collector network access. Use port-forward for inspection or explicitly allow a monitoring namespace before installing a collector.

Log Analytics is configured for AKS container insights. No alert rules, distributed tracing, retention cost limit, or operational SLO is implemented.

## Production evolution

Use managed PostgreSQL with restore testing, externalized secrets, authentication, private networking decisions, TLS, connection pooling, proper application serving, explicit schema migrations, release approval policy, tested rollback compatibility, registry immutability, image scanning, and measured capacity/SLOs before treating this as production infrastructure.

## Primary references

- [AKS Terraform resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster)
- [AKS kubelogin](https://learn.microsoft.com/azure/aks/kubelogin-authentication)
- [Kubernetes probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Kubernetes network policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Azure OIDC for GitHub Actions](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure)
