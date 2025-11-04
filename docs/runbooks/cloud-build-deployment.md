# Runbook: Deploying with Cloud Build

This runbook provides the steps to deploy the Nemo Compliance MVP using the `cloudbuild.yaml` file. This method is recommended to avoid local environment issues.

## 1. Prerequisites

- You have `gcloud` CLI installed and authenticated.
- Your project has the Cloud Build API enabled.
- Cloud Build service account has required permissions (see `docs/runbooks/grant-cloud-build-permissions.md`). At minimum:
  - `roles/cloudfunctions.developer` on the project
  - `roles/run.admin` on the project
  - `roles/iam.serviceAccountUser` on `day-planner-london-mvp@appspot.gserviceaccount.com`

The `cloudbuild.yaml` includes a preflight step that checks these permissions using `deploy/verify-cloud-build-permissions.sh` and deploys functions with the explicit runtime service account `day-planner-london-mvp@appspot.gserviceaccount.com`.

## 2. Deployment Steps

1.  **Navigate to the Project Root:**
    *   Open your terminal and navigate to the root of the Nemo project directory.

2.  **Submit the Build to Cloud Build:**
    *   Run the following command to start the deployment:
        ```bash
        gcloud builds submit --config cloudbuild.yaml .
        ```

3.  **Monitor the Build:**
    *   You can monitor the progress of the build in the [Google Cloud Console](https://console.cloud.google.com/cloud-build).
    *   The build will execute all the steps defined in the `cloudbuild.yaml` file, including:
        *   Enabling APIs
        *   Creating GCS buckets
        *   Creating secrets
        *   Deploying Cloud Functions

## 3. Post-Deployment Steps

After the Cloud Build job completes successfully, you will still need to perform the following manual steps, as outlined in the `docs/DEPLOYMENT_GUIDE.md`:

1.  **Set Up Vertex AI Vector Search:**
    *   Run the `./deploy/setup-vertex-ai.sh` script.
2.  **Update Function Configuration:**
    *   Update the `nemo-query` and `nemo-ingest` functions with the Vertex AI index and endpoint IDs.
3.  **Set Up Google Custom Search Engine:**
    *   Update the `google-cse-id` and `google-api-key` secrets with your actual values.
4.  **Configure Automated Ingestion:**
    *   Run the `./deploy/setup-scheduler.sh` script.
5.  **Deploy Frontend:**
    *   Deploy the frontend using either Firebase Hosting or Google Cloud Storage.

This runbook provides a reliable and repeatable process for deploying the Nemo application.
