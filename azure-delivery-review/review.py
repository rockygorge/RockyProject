"""Review declared delivery controls. Does not inspect live infrastructure."""
import argparse
import json
import sys
from pathlib import Path

CONTROLS = (
    ("terraform_validation", "Validate Terraform before deployment."),
    ("plan_review", "Review a Terraform plan before applying."),
    ("short_lived_auth", "Use short-lived authentication for cloud access."),
    ("restricted_permissions", "Restrict deployment permissions to required scope."),
    ("deployment_approval", "Require an approval before deployment."),
    ("recovery_plan", "Document and test a recovery plan."),
)

def review(config):
    if not isinstance(config, dict):
        raise ValueError("configuration must be a JSON object")
    return [{"control": key, "status": "declared" if config.get(key) is True else "needs review",
             "recommendation": message} for key, message in CONTROLS]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        findings = review(config)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print("Declaration review only; controls are not independently verified.\n")
    for finding in findings:
        print(f"{finding['status'].upper():12} {finding['control']}: {finding['recommendation']}")
    return 1 if any(f["status"] == "needs review" for f in findings) else 0

if __name__ == "__main__":
    sys.exit(main())
