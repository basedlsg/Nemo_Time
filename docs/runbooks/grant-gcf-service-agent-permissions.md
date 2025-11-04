# Runbook: Grant Cloud Functions Service Agent Permissions

Cloud Functions 2nd gen uses the Cloud Functions Service Agent to create and configure Cloud Run services. When deploying with `--allow-unauthenticated`, it must set the Cloud Run service IAM policy. If it lacks permissions, deployments fail with:

```
Permission 'run.services.setIamPolicy' denied on resource '.../services/<name>'
```

## Required Role

- Project → `service-PROJECT_NUMBER@gcf-admin-robot.iam.gserviceaccount.com`
  - `roles/run.admin`

## Grant via script (recommended)

```bash
./deploy/grant-gcf-service-agent-permissions.sh
```

## Grant via gcloud (manual)

```bash
PROJECT_ID=day-planner-london-mvp
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
GCF_SA="service-${PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${GCF_SA}" \
  --role roles/run.admin
```

## Verification

Re-run the permission verifier which now also checks the service agent:

```bash
./deploy/verify-cloud-build-permissions.sh
```

