# Security

## SECRET_KEY rotation

A compromised SECRET_KEY must be treated as invalid.

The application no longer contains the old hard-coded secret. Production now requires SECRET_KEY to be supplied through the environment.

Generate a new secret:

    python -c "import secrets; print(secrets.token_hex(32))"

Then replace the production SECRET_KEY in the deployment environment.

Do not place the new value in:

- Git
- README files
- .env.example
- source code
- issue comments
- pull request comments

Restart the production application after changing the secret.

## Git history

Removing a secret from the latest source file does not remove it from old Git commits.

Because the old secret was previously committed, it must not be trusted again even if it is no longer present in the current source.

If repository history must also be cleaned, use a controlled Git history rewrite and coordinate it with every clone and deployment.

## Database

Production must provide DATABASE_URL.

The application now refuses to start with ProductionConfig when DATABASE_URL is missing.

Use PostgreSQL for production.

## Cookies

Production should use:

    SESSION_COOKIE_SECURE=True

when the application is served over HTTPS.