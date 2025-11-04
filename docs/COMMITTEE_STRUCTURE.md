# Nemo Deployment - Committee Structure and Roles

This document outlines the committee structure for the Nemo Compliance MVP deployment. Each committee has a specific set of responsibilities and operates in a designated mode to ensure a streamlined and efficient deployment process.

## 1. Committee Overview

| Committee Name | Primary Mode | Core Responsibilities |
| :--- | :--- | :--- |
| **Steering Committee** | 🏗️ `Architect` | Overall project governance, planning, and final approvals. |
| **Google Cloud Committee** | 🤖 `Google GenAI Developer` | Implementation and configuration of all Google Cloud services. |
| **Core Infrastructure Committee** | 💻 `Code` | Deployment of Cloud Functions and core application infrastructure. |
| **Frontend & Validation Committee** | 💻 `Code` / 🪲 `Debug` | Frontend deployment, end-to-end testing, and final validation. |

## 2. Committee Details

### 2.1. Steering Committee

*   **Primary Mode:** 🏗️ `Architect`
*   **Responsibilities:**
    *   Define and approve the overall deployment plan and timeline.
    *   Establish and maintain the committee structure and roles.
    *   Create and manage runbooks, checklists, and worklogs.
    *   Provide final approval for each phase of the deployment.
    *   Serve as the central point of contact for all deployment-related activities.

### 2.2. Google Cloud Committee

*   **Primary Mode:** 🤖 `Google GenAI Developer`
*   **Responsibilities:**
    *   Set up and configure all required Google Cloud services, including Vertex AI, Document AI, and Google Custom Search Engine.
    *   Manage all API keys, secrets, and service accounts.
    *   Run integration tests to ensure that all Google Cloud services are functioning correctly.
    *   Provide support and guidance to other committees on Google Cloud-related issues.

### 2.3. Core Infrastructure Committee

*   **Primary Mode:** 💻 `Code`
*   **Responsibilities:**
    *   Execute the deployment scripts to deploy the `health`, `query`, and `ingest` Cloud Functions.
    *   Update and manage all function configurations and environment variables.
    *   Run health checks and other tests to validate the core infrastructure deployment.
    *   Troubleshoot and resolve any issues related to the Cloud Function deployments.

### 2.4. Frontend & Validation Committee

*   **Primary Mode:** 💻 `Code` / 🪲 `Debug`
*   **Responsibilities:**
    *   Deploy the frontend application using the chosen hosting option (Firebase Hosting or GCS).
    *   Conduct comprehensive end-to-end testing to validate the entire application workflow.
    *   Complete the production readiness checklist, ensuring that the application is secure, performant, and operationally ready.
    *   Manage the final release process and monitor the application post-deployment.

This structure ensures a clear separation of duties and allows each committee to focus on its area of expertise, leading to a more efficient and successful deployment.