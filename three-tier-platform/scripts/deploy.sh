#!/usr/bin/env bash
set -euo pipefail
: "${REGISTRY_SERVER:?Set REGISTRY_SERVER}"
: "${IMAGE_TAG:?Set IMAGE_TAG to the source commit SHA}"
: "${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD}"
[[ "$IMAGE_TAG" =~ ^[a-f0-9]{40}$ ]] || { echo "Use a full commit SHA image tag"; exit 1; }
[[ "$REGISTRY_SERVER" =~ ^[a-z0-9]+\.azurecr\.io$ ]] || { echo "Expected Azure registry hostname"; exit 1; }
[[ "$POSTGRES_PASSWORD" =~ ^[a-zA-Z0-9]{24,}$ ]] || { echo "Use 24+ alphanumeric password characters"; exit 1; }
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
kubectl apply -f "$project_dir/k8s/namespace.yaml"
# Never rotate a live database password merely by changing a Kubernetes Secret.
if kubectl -n platformops get secret database >/dev/null 2>&1; then
  existing="$(kubectl -n platformops get secret database -o jsonpath='{.data.password}' | base64 --decode)"
  [[ "$existing" == "$POSTGRES_PASSWORD" ]] || { echo "Existing DB password differs; follow rotation runbook."; exit 1; }
  unset existing
else
  kubectl -n platformops create secret generic database \
    --from-literal="password=$POSTGRES_PASSWORD" \
    --from-literal="url=postgresql://platformops:$POSTGRES_PASSWORD@postgres:5432/platformops" \
    --dry-run=client -o yaml | kubectl apply -f -
fi
kubectl apply -f "$project_dir/k8s/network-policy.yaml"
kubectl apply -f "$project_dir/k8s/postgres.yaml"
kubectl -n platformops rollout status statefulset/postgres --timeout=240s
# Render images into temporary manifests before apply, avoiding placeholder-image rollouts.
rendered="$(mktemp -d)"
trap 'rm -rf "$rendered"' EXIT
for component in api web; do
  sed "s|platformops-$component:local|$REGISTRY_SERVER/platformops-$component:$IMAGE_TAG|g" \
    "$project_dir/k8s/$component.yaml" > "$rendered/$component.yaml"
done
kubectl apply -f "$rendered/api.yaml"
kubectl -n platformops rollout status deployment/api --timeout=240s
kubectl apply -f "$rendered/web.yaml"
kubectl -n platformops rollout status deployment/web --timeout=180s
echo "Rollouts completed. Run: kubectl -n platformops port-forward svc/web 8080:8080"
