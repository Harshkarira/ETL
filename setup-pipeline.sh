#!/bin/bash


TARGET="tutorial"              
PIPELINE_NAME="reliance-etl"   
PIPELINE_FILE="pipeline.yml"   
CONCOURSE_URL="http://localhost:8081"
USERNAME="test"                
PASSWORD="test"     

if ! command -v fly &> /dev/null; then
    echo "Error: 'fly' CLI is not installed. Please install it first."
    echo "Download it from your Concourse UI at $CONCOURSE_URL or follow the official docs."
    exit 1
fi

echo "Logging in to Concourse at $CONCOURSE_URL..."
fly -t "$TARGET" login -c "$CONCOURSE_URL" -u "$USERNAME" -p "$PASSWORD"
if [ $? -ne 0 ]; then
    echo "Error: Failed to log in to Concourse. Check URL, username, and password."
    exit 1
fi

echo "Syncing fly CLI with Concourse..."
fly -t "$TARGET" sync
if [ $? -ne 0 ]; then
    echo "Error: Failed to sync fly CLI."
    exit 1
fi

echo "Setting pipeline '$PIPELINE_NAME' from $PIPELINE_FILE..."
fly -t "$TARGET" set-pipeline -p "$PIPELINE_NAME" -c "$PIPELINE_FILE" --non-interactive
if [ $? -ne 0 ]; then
    echo "Error: Failed to set pipeline. Check $PIPELINE_FILE for syntax errors."
    exit 1
fi

echo "Unpausing pipeline '$PIPELINE_NAME'..."
fly -t "$TARGET" unpause-pipeline -p "$PIPELINE_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to unpause pipeline."
    exit 1
fi

echo "Triggering job 'download-reliance-data' in pipeline '$PIPELINE_NAME'..."
fly -t "$TARGET" trigger-job -j "$PIPELINE_NAME/download-reliance-data"
if [ $? -ne 0 ]; then
    echo "Error: Failed to trigger job."
    exit 1
fi