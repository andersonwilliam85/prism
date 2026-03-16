# Acme Corp Prism

**Version:** 2.0.0
**Type:** Mid-size company (~200 engineers)

Development environment configuration for Acme Corp, a mid-size company standardizing its engineering practices during a monolith-to-microservices migration.

## What It Covers

- **AWS-first cloud setup** with SSO authentication for dev/staging/prod accounts
- **Monolith migration context** so new engineers understand the Django-to-microservices transition
- **5 team configs** with real repo lists, tech stacks, and day-one checklists
- **CI/CD via GitHub Actions** with shared workflow templates
- **Internal registries** for npm (@acme scope), Docker (ECR), and PyPI
- **Security basics** (Dependabot, gitleaks pre-commit, Okta SSO + MFA)

## Teams

| Team | Size | Focus |
|------|------|-------|
| Platform | 8 | AWS infra, ECS-to-EKS migration, CI/CD, observability |
| Backend | 25 | Monolith, microservices, APIs, databases |
| Frontend | 15 | Next.js web app, design system, accessibility |
| Data | 10 | Snowflake warehouse, Airflow pipelines, ML experiments |
| Mobile | 8 | React Native iOS/Android apps |

## Package Structure

```
acme-corp.prism/
  package.yaml          Package metadata and team selection
  welcome.yaml          Onboarding welcome page
  resources.yaml        Links to internal tools and docs
  base/
    acme-corp.yaml      Company-wide: git, AWS, registries, workspace layout
    tool-registry.yaml  Tools not in the base prism registry
  teams/
    platform-team.yaml  Platform team repos, tools, projects
    backend-team.yaml   Backend team + monolith migration guide
    frontend-team.yaml  Frontend team + Next.js migration
    data-team.yaml      Data team + Snowflake/dbt/Airflow
    mobile-team.yaml    Mobile team + React Native setup
```
