#!/usr/bin/env bash
set -euo pipefail

# Verifies that the Cloud Build service account has the roles required to deploy
# Cloud Functions (Gen 2) with --allow-unauthenticated.

PROJECT_ID=${PROJECT_ID:-day-planner-london-mvp}
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
RUNTIME_SA="${PROJECT_ID}@appspot.gserviceaccount.com"
GCF_SA="service-${PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com"
CR_SA="service-${PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com"

echo "Project:        $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "CB SA:         $CB_SA"
echo "Runtime SA:    $RUNTIME_SA"
echo "GCF Service SA:$GCF_SA"
echo "Cloud Run SA: $CR_SA"

missing=()

has_binding() {
  local scope=$1 # projects/<id> or serviceAccounts/<email>
  local role=$2
  local member=$3
  if [[ $scope == projects/* ]]; then
    gcloud projects get-iam-policy "${scope#projects/}" \
      --flatten="bindings[].members" \
      --format="value(bindings.role,bindings.members)" 2>/dev/null | \
      grep -q "^${role}[[:space:]]*${member}$"
  else
    gcloud iam service-accounts get-iam-policy "${scope#serviceAccounts/}" \
      --flatten="bindings[].members" \
      --format="value(bindings.role,bindings.members)" 2>/dev/null | \
      grep -q "^${role}[[:space:]]*${member}$"
  fi
}

member="serviceAccount:${CB_SA}"

echo "\nChecking project-level roles on ${PROJECT_ID}..."
for role in roles/cloudfunctions.developer roles/run.admin; do
  if has_binding "projects/${PROJECT_ID}" "$role" "$member"; then
    echo "✔ $role present"
  else
    echo "✖ $role MISSING"
    missing+=("Project ${role}")
  fi
done

echo "\nChecking Service Account User on runtime SA..."
if has_binding "serviceAccounts/${RUNTIME_SA}" roles/iam.serviceAccountUser "$member"; then
  echo "✔ roles/iam.serviceAccountUser on ${RUNTIME_SA} present"
else
  echo "✖ roles/iam.serviceAccountUser on ${RUNTIME_SA} MISSING"
  missing+=("SA User on ${RUNTIME_SA}")
fi

echo "\nChecking Cloud Functions Service Agent permissions for Cloud Run..."
if has_binding "projects/${PROJECT_ID}" roles/run.admin "serviceAccount:${GCF_SA}"; then
  echo "✔ roles/run.admin on project for ${GCF_SA} present"
else
  echo "✖ roles/run.admin on project for ${GCF_SA} MISSING"
  missing+=("Run Admin for ${GCF_SA}")
fi

echo "\nChecking Cloud Run Service Agent permissions..."
if has_binding "projects/${PROJECT_ID}" roles/run.admin "serviceAccount:${CR_SA}"; then
  echo "✔ roles/run.admin on project for ${CR_SA} present"
else
  echo "✖ roles/run.admin on project for ${CR_SA} MISSING (run.serviceAgent is typical; admin may be needed in some orgs)"
fi

if (( ${#missing[@]} > 0 )); then
  echo "\nOne or more required permissions are missing:"
  printf ' - %s\n' "${missing[@]}"
  echo "\nPlease follow docs/runbooks/grant-cloud-build-permissions.md to grant the required roles, then retry the build."
  exit 1
fi

echo "\nAll required permissions are present."
