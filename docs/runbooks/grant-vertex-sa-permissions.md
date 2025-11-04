# Runbook: Grant Vertex AI Permissions to GCS Bucket

This runbook provides manual steps to resolve the `FAILED_PRECONDITION` error that occurs when the Vertex AI service account lacks permissions to read from a GCS bucket during index creation.

## 1. The Problem

When running `./deploy/setup-vertex-ai.sh`, the command fails with an error similar to this:

```
ERROR: (gcloud.ai.indexes.create) FAILED_PRECONDITION: Service account `service-xxxxxxxxxxxx@gcp-sa-aiplatform.iam.gserviceaccount.com` does not have `[storage.buckets.get, storage.objects.get]` IAM permission(s) to the bucket "day-planner-london-mvp-nemo-clean".
```

This means the automated script is unable to grant the required permissions, and you must do it manually.

## 2. Required Information

*   **Project ID:** `day-planner-london-mvp`
*   **Bucket Name:** `day-planner-london-mvp-nemo-clean`
*   **Service Account Email:** `service-612990030705@gcp-sa-aiplatform.iam.gserviceaccount.com`

## 3. Manual Remediation Steps

Please follow these steps in the Google Cloud Console:

1.  **Navigate to the Cloud Storage Browser:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   In the navigation menu, select **Cloud Storage** > **Buckets**.

2.  **Select the Correct Bucket:**
    *   In the list of buckets, find and click on the bucket named `day-planner-london-mvp-nemo-clean`.

3.  **Go to the Permissions Tab:**
    *   Click on the **PERMISSIONS** tab for the selected bucket.

4.  **Grant Access:**
    *   Click the **+ GRANT ACCESS** button. This will open a new panel on the right.

5.  **Configure the New Principal:**
    *   In the **New principals** field, paste the full service account email:
        ```
        service-612990030705@gcp-sa-aiplatform.iam.gserviceaccount.com
        ```
    *   In the **Select a role** dropdown, search for and select the **Storage Object Viewer** role (`roles/storage.objectViewer`). This role includes the `storage.objects.get` permission.

6.  **Save the Changes:**
    *   Click the **SAVE** button.

## 4. Verification

After completing these steps, the permissions should be correctly configured. The AI model will then re-run the `setup-vertex-ai.sh` script to proceed with the deployment.