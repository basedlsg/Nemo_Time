#!/bin/bash

# Quick deployment status check
PROJECT_ID="day-planner-london-mvp"
REGION="asia-east2"

echo "🔍 Checking deployment status for project: $PROJECT_ID"
echo ""

echo "📋 Checking Cloud Functions..."
gcloud functions list --region=$REGION --format="table(name,status,updateTime)" 2>/dev/null || echo "No functions found yet or still deploying..."

echo ""
echo "🔐 Checking secrets..."
gcloud secrets list --format="table(name,createTime)" 2>/dev/null || echo "No secrets found"

echo ""
echo "📊 Checking enabled APIs..."
gcloud services list --enabled --filter="name:cloudfunctions OR name:aiplatform OR name:documentai" --format="table(name,title)" 2>/dev/null

echo ""
echo "✅ Status check complete"