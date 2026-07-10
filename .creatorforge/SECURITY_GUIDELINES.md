# Security Guidelines

## Input Validation

Validate API request fields, lengths, allowed model values, project IDs, and filesystem-derived values before use.

## Output Validation

Treat model output as untrusted until it meets the expected artifact format. Use lightweight cleanup now; add stronger validation only through approved work.

## Secrets and API Keys

Never hard-code secrets or API keys. Do not log them, include them in prompts, or commit them to Git.

## Environment Variables

Use documented environment variables for deployment-specific configuration. Keep `.env` files out of version control.

## Logging

Log only what is necessary to diagnose failures. Avoid full creator content, prompts, generated artifacts, credentials, and personal data.

## Dependency Updates

Review and update dependencies regularly. Prioritize security fixes and verify compatibility after upgrades.

## Local AI Privacy

Local Ollama is a privacy advantage, not a guarantee. Protect the host, local project files, backups, and any future network exposure.

## Git Secrets

Use `.gitignore`, pre-commit checks when available, and code review to prevent credentials, tokens, private outputs, and environment files from entering Git history.
