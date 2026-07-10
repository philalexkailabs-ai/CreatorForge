# Deployment Strategy

## Local Development

The primary current environment is local development: FastAPI, static frontend assets, local Ollama, and local `outputs/` storage.

## Docker

Future containers should package the API and frontend runtime predictably. Ollama model storage and hardware acceleration require deliberate host integration and should not be assumed.

## Linux Server

A future Linux deployment should use a dedicated service account, restricted filesystem permissions, managed environment variables, backups, and process supervision.

## Cloud VM

A cloud VM is appropriate only when the privacy, model-hosting, cost, and user-access implications are approved. Local-first remains the baseline.

## Reverse Proxy

Use a reverse proxy in hosted deployment to serve static assets, route API traffic, limit request size, and provide TLS termination.

## HTTPS

Require HTTPS for all hosted environments. Redirect HTTP and manage certificate renewal.

## Environment Variables

Move deployment-sensitive settings to documented environment variables. Never commit secrets, private endpoints, or production credentials.

## Backups

Back up project metadata and creator artifacts. Test restoration, not just backup creation.

## Monitoring

Monitor availability, request duration, model failures, storage health, and resource use while preserving creator privacy.

## Logging

Use structured, minimal logs. Avoid logging full prompts, research, generated scripts, API keys, or other creator content by default.

## Scaling

Scale only after measuring demand. The current in-memory progress design is single-process and must be redesigned before multi-instance deployment.
