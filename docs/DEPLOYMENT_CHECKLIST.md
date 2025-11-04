# Nemo Deployment - Master Checklist

This document provides the master checklist for the Nemo Compliance MVP deployment. Each phase must be completed in order, and all tasks within a phase must be checked off before proceeding to the next.

## Phase 1: Pre-Deployment Setup (Architect Mode)

*   [x] **Task 1.1:** Define committee structure and roles.
*   [ ] **Task 1.2:** Finalize deployment checklist and runbooks.
*   [ ] **Task 1.3:** Create a worklog for the deployment process.

## Phase 2: Google Services Implementation (Google GenAI Developer Mode)

*   [ ] **Task 2.1:** Set up and configure Vertex AI, Document AI, and Google CSE.
    *   [ ] Create Vertex AI Index and Endpoint.
    *   [ ] Create Document AI Processor.
    *   [ ] Configure Google Custom Search Engine.
*   [ ] **Task 2.2:** Update secrets with the correct API keys and IDs.
    *   [ ] Update `google-cse-id` secret.
    *   [ ] Update `google-api-key` secret.
*   [ ] **Task 2.3:** Run integration tests to validate Google services.
    *   [ ] Run `test_cse.py`.
    *   [ ] Run `test_docai.py`.
    *   [ ] Run `test_vertex_index.py`.

## Phase 3: Core Infrastructure Deployment (Code Mode)

*   [ ] **Task 3.1:** Execute the main deployment script to deploy Cloud Functions.
    *   [ ] Run `deploy/deploy.sh`.
*   [ ] **Task 3.2:** Update function configurations with the correct environment variables.
    *   [ ] Update `nemo-query` with Vertex AI IDs.
    *   [ ] Update `nemo-ingest` with Vertex AI and Document AI IDs.
*   [ ] **Task 3.3:** Run health checks to verify the deployment.
    *   [ ] `curl` the `nemo-health` endpoint.

## Phase 4: Frontend Deployment and Final Validation (Code Mode)

*   [ ] **Task 4.1:** Deploy the frontend application.
    *   [ ] Choose hosting option (Firebase or GCS).
    *   [ ] Update `index.html` with API URLs.
    *   [ ] Run deployment command.
*   [ ] **Task 4.2:** Run end-to-end tests to validate the entire application.
    *   [ ] Run `tests/integration/test_end_to_end.py`.
*   [ ] **Task 4.3:** Complete the production readiness checklist.
    *   [ ] Review and confirm all items in the `docs/DEPLOYMENT_GUIDE.md` checklist.

This checklist will be updated as each task is completed, providing a real-time view of the deployment progress.