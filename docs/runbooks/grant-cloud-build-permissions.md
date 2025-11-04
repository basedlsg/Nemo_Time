# Runbook: Grant Cloud Build Permissions

This runbook provides manual steps to resolve the `run.services.setIamPolicy` (and similar) errors when the Cloud Build service account lacks the necessary permissions to deploy Cloud Functions (Gen 2) and set unauthenticated access.

## 1. Background

Cloud Functions Gen 2 runs on Cloud Run. Deployments that pass `--allow-unauthenticated` need permission to set the Cloud Run service IAM policy (`run.services.setIamPolicy`). The default Cloud Build service account usually is:

- `PROJECT_NUMBER@cloudbuild.gserviceaccount.com`

It needs specific roles to deploy successfully.

## 2. Identify the Principals

- Project ID: `day-planner-london-mvp`
- Project number: find with:
  ```bash
  gcloud projects describe day-planner-london-mvp --format='value(projectNumber)'
  ```
- Cloud Build service account (CB SA): `PROJECT_NUMBER@cloudbuild.gserviceaccount.com`
- Cloud Functions runtime service account (Runtime SA): `day-planner-london-mvp@appspot.gserviceaccount.com`

## 3. Required Roles

Grant these roles with the principle of least privilege:

- On the PROJECT to CB SA:
  - Cloud Functions Developer: `roles/cloudfunctions.developer`
  - Cloud Run Admin: `roles/run.admin` (needed for `run.services.setIamPolicy`)

- On the Runtime SA to CB SA:
  - Service Account User: `roles/iam.serviceAccountUser`

Note: You should not grant broad roles like Project IAM Admin to the Cloud Build service account.

## 4. Grant via script (recommended)

Run this helper script as a project owner:

```bash
./deploy/grant-cloud-build-permissions.sh
```

This grants the minimum roles listed above using the App Engine default service account as the runtime SA (which is also set explicitly in `cloudbuild.yaml`).

## 5. Grant via gcloud (manual)

```bash
PROJECT_ID=day-planner-london-mvp
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
RUNTIME_SA="${PROJECT_ID}@appspot.gserviceaccount.com"

# Project-level roles
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${CB_SA}" \
  --role roles/cloudfunctions.developer

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${CB_SA}" \
  --role roles/run.admin

# Allow Cloud Build to act as the runtime SA used by Cloud Functions
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA" \
  --member "serviceAccount:${CB_SA}" \
  --role roles/iam.serviceAccountUser
```

## 6. Grant via Console

1. Go to IAM & Admin > IAM for the project `day-planner-london-mvp`.
2. Click + Grant Access and add principal `PROJECT_NUMBER@cloudbuild.gserviceaccount.com` with roles:
   - Cloud Functions Developer
   - Cloud Run Admin
3. Go to IAM & Admin > Service Accounts, locate `day-planner-london-mvp@appspot.gserviceaccount.com`.
4. Open the Permissions tab and Grant Access: add principal `PROJECT_NUMBER@cloudbuild.gserviceaccount.com` with role Service Account User.

## 7. Verification

Re-run the build:
```bash
gcloud builds submit --config cloudbuild.yaml .
```

If it still fails, run `deploy/verify-cloud-build-permissions.sh` locally (or inspect its Cloud Build output) to confirm all roles are present.
