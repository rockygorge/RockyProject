# Azure Delivery Review

A proposed command-line tool for reviewing infrastructure delivery readiness. This is a project outline, not a completed implementation.

## Problem

Teams need a repeatable way to identify missing checks before releasing cloud infrastructure. A small, local tool can highlight review items without needing Azure access.

## Proposed scope

- Read a sample deployment configuration and report missing validation, approval, identity and recovery settings.
- Generate a human-readable report with actionable findings.
- Include automated tests and a GitHub Actions validation workflow.
- Document trade-offs, limitations and an example review.

## Design boundaries

This tool would inspect declared configuration only. It would not verify actual Azure resources, permissions, compliance, or security, and it would not deploy anything. Example configurations would use fictitious values.

## Project status

Planning only. Implementation, tests and CI have not been completed. This AI-assisted portfolio project will be developed as a standalone repository so it can be pinned separately.

## Next step

Implement a small working version, run its tests, and publish only verified results. No customer configuration or credentials belong in this public project.
