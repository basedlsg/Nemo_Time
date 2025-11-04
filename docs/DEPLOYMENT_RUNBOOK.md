# Nemo Deployment - Runbook

This runbook provides troubleshooting and remediation steps for common issues that may arise during the Nemo Compliance MVP deployment.

## 1. Cloud Function Deployment Failures

*   **Symptom:** The `gcloud functions deploy` command fails with a permission-denied error.
*   **Cause:** The user or service account running the deployment script lacks the necessary IAM roles.
*   **Remediation:**
    1.  Ensure the active `gcloud` user has the `Cloud Functions Admin` and `Service Account User` roles.
    2.  Verify that the Cloud Functions service account (`PROJECT_ID@appspot.gserviceaccount.com`) has the `Editor` role.

*   **Symptom:** The deployment fails with a source code upload error.
*   **Cause:** Network connectivity issues or problems with the Cloud Storage bucket used for staging.
*   **Remediation:**
    1.  Check network connectivity and retry the deployment.
    2.  Ensure the Cloud Build API is enabled.
    3.  Manually clear the staging bucket: `gsutil rm -r gs://PROJECT_ID_cloudbuild/source/*`.

## 2. Health Check Endpoint (`/health`) Failures

*   **Symptom:** The health check endpoint returns a `500 Internal Server Error`.
*   **Cause:** The `nemo-health` function is unable to connect to one of its dependent services (Vertex AI, GCS, or Secret Manager).
*   **Remediation:**
    1.  Check the function's logs for specific error messages: `gcloud functions logs read nemo-health --region=REGION`.
    2.  Verify that the Vertex AI index and endpoint are deployed and healthy.
    3.  Ensure the GCS buckets (`nemo-raw`, `nemo-clean`) exist and are accessible.
    4.  Confirm that all required secrets have been created in Secret Manager.

## 3. Query Endpoint (`/query`) Failures

*   **Symptom:** The query endpoint returns an empty response or a `500` error.
*   **Cause:** Issues with the Vertex AI index, the `nemo-query` function's configuration, or the initial data ingestion.
*   **Remediation:**
    1.  Check the `nemo-query` function's logs for errors.
    2.  Verify that the `VERTEX_INDEX_ID` and `VERTEX_ENDPOINT_ID` environment variables are correctly set.
    3.  Ensure that the initial data ingestion has been completed successfully.
    4.  Test the Vertex AI index directly using the Google Cloud Console to confirm it is returning results.

## 4. Ingestion Process (`/ingest`) Failures

*   **Symptom:** The ingestion process fails to discover or process documents.
*   **Cause:** Problems with the Google Custom Search Engine (CSE) configuration, Document AI, or GCS bucket permissions.
*   **Remediation:**
    1.  Check the `nemo-ingest` function's logs for detailed error messages.
    2.  Verify that the `google-cse-id` and `google-api-key` secrets are correct.
    3.  Ensure the Document AI processor is created and the `DOCAI_PROCESSOR_ID` is correctly set.
    4.  Confirm that the Cloud Functions service account has `Storage Object Admin` permissions on the `nemo-raw` and `nemo-clean` buckets.

This runbook will be updated as new issues and resolutions are identified.