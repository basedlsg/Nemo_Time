# Error Report: Nemo Compliance MVP Deployment

## 1. Executive Summary

This report provides a detailed analysis of the persistent errors encountered during the deployment of the Nemo Compliance MVP. The primary issue is a series of permission-denied errors originating from the Cloud Build environment, which are preventing the successful deployment of the application's core infrastructure.

## 2. Timeline of Events

1.  **Initial Deployment Attempts:** The initial deployment attempts were made using local scripts (`deploy/setup-vertex-ai.sh`, `deploy/grant-permissions.sh`). These attempts failed due to timeouts and network-related issues, indicating a problem with the local development environment's connectivity to Google Cloud.
2.  **Shift to Cloud Build:** To bypass the local environment issues, the deployment strategy was shifted to use Cloud Build. A `cloudbuild.yaml` file was created to automate the deployment process within Google Cloud's infrastructure.
3.  **Cloud Build Failures:** The Cloud Build jobs have failed consistently with a `Permission 'run.services.setIamPolicy' denied` error. This indicates that the Cloud Build service account lacks the necessary permissions to deploy Cloud Functions.
4.  **Remediation Attempts:** Several attempts were made to resolve the permissions issue by modifying the `cloudbuild.yaml` file to grant the `Cloud Functions Admin` and `Editor` roles to the Cloud Build service account. These attempts have been unsuccessful, as the Cloud Build service account does not have permission to modify IAM policies.

## 3. Root Cause Analysis

The root cause of the deployment failures is a classic chicken-and-egg problem:

*   The Cloud Build service account needs the `Cloud Functions Admin` role to deploy the Cloud Functions.
*   However, the Cloud Build service account does not have the `Project IAM Admin` role, so it cannot grant itself the `Cloud Functions Admin` role.

This is a security measure to prevent a service account from escalating its own privileges.

## 4. Current Status

The deployment is currently blocked. The `cloudbuild.yaml` file is configured to deploy the application, but it will continue to fail until the Cloud Build service account is granted the necessary permissions.

## 5. Recommended Next Steps

To resolve this issue, a project owner must manually grant the correct permissions to the Cloud Build service account used for deployment (Gen 2 on Cloud Run requires Cloud Run Admin to set unauthenticated access):

- On the project to `PROJECT_NUMBER@cloudbuild.gserviceaccount.com`:
  - `roles/cloudfunctions.developer`
  - `roles/run.admin`
- On the runtime service account `day-planner-london-mvp@appspot.gserviceaccount.com` to the same principal:
  - `roles/iam.serviceAccountUser`

Follow the runbook for exact commands:

* `docs/runbooks/grant-cloud-build-permissions.md`

After applying these permissions, re-run:

```
gcloud builds submit --config cloudbuild.yaml .
```

If deployment still fails with `run.services.setIamPolicy` on the Cloud Run service, also grant Cloud Run Admin to the Cloud Functions Service Agent:

- On the project to `service-PROJECT_NUMBER@gcf-admin-robot.iam.gserviceaccount.com`:
  - `roles/run.admin`

See: `docs/runbooks/grant-gcf-service-agent-permissions.md`.
