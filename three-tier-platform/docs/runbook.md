# Operations runbook

## Daily inspection

```bash
kubectl -n platformops get deploy,statefulsets,pods,svc,pvc,hpa,pdb
kubectl -n platformops get events --sort-by=.metadata.creationTimestamp
kubectl -n platformops logs deployment/api --tail=100
```

Inspect /metrics separately:

```bash
kubectl -n platformops port-forward svc/api 8000:8000
curl --fail http://127.0.0.1:8000/metrics
```

## Troubleshooting

| Symptom | First checks | Likely path |
| --- | --- | --- |
| ImagePullBackOff | Image SHA exists in ACR; inspect pod events | Correct registry/image reference; verify kubelet AcrPull propagation |
| PVC Pending | Default StorageClass, CSI driver, disk quota, events | Fix storage provisioning before restarting apps |
| PostgreSQL cannot initialize | Pod events and logs, volume ownership | Verify fsGroup/UID/storage permissions; do not delete PVC to hide errors |
| API unready | Database readiness, Secret, network policy, API logs | Restore database connectivity and correct credentials |
| OIDC login fails | Exact repo/environment subject and audience | Repair federation; do not add a client secret as a workaround |
| kubectl forbidden | Entra object ID and both AKS role assignments | Check cluster user and RBAC roles; allow propagation time |
| Nginx returns 502 | API endpoints, API readiness, network policies | Fix API tier first |
| HPA unknown | metrics-server and resource requests | Verify metrics availability; HPA is not a substitute for load testing |
| Pipeline password mismatch | Existing Secret vs GitHub environment secret | Follow deliberate database credential rotation; avoid overwriting the Secret |

## Observe a database outage

Only in a disposable lab:

1. Create a task through the UI and record its ID.
2. Scale PostgreSQL to zero; inspect API readiness. Liveness should still succeed.
3. Restore PostgreSQL to one replica and wait for rollout.
4. Refresh the UI and verify the original task still exists.

```bash
kubectl -n platformops scale statefulset/postgres --replicas=0
kubectl -n platformops get pods
kubectl -n platformops scale statefulset/postgres --replicas=1
kubectl -n platformops rollout status statefulset/postgres --timeout=240s
```

The single-instance database makes this an availability interruption. It is a failure demonstration, not an HA recovery claim.

## Roll back application code

Inspect history first:

```bash
kubectl -n platformops rollout history deployment/api
kubectl -n platformops rollout undo deployment/api
kubectl -n platformops rollout status deployment/api --timeout=240s
```

Roll back web separately only if needed. Kubernetes rollout undo does not restore database data, credentials, schema, infrastructure, or guarantee old/new compatibility. There is no automatic rollback in the pipeline.

## Database credentials

Do not change POSTGRES_PASSWORD on an existing volume and expect PostgreSQL to update its role. The deploy script rejects a mismatched existing Secret. For real rotation, coordinate the PostgreSQL role password, the Secret URL/password values, and an API rollout in a maintenance plan. This lab supplies no automatic rotation script.

## Cleanup

- Compose: docker compose down retains data; docker compose down --volumes deletes it.
- Kubernetes: deleting a StatefulSet does not necessarily remove its PVC. Explicitly review PVC and disk retention before removal.
- Azure: run the manual infrastructure workflow with destroy and review the generated destroy plan. This removes the lab cluster and its application data; there is no backup.
- Confirm all lab-owned disks and resources were removed. The pre-existing backend and federated identity remain outside this stack.
- Never delete the Terraform backend before destroying the managed infrastructure.
