# RetailOS Server

RetailOS is a Flask backend for retail product, inventory, sales and customer management.

## Development

Set a secret before starting the application:

    export SECRET_KEY="your-secret"

For PostgreSQL:

    export DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/retailos"

Install dependencies:

    pip install -r server/requirements.txt

## Testing

Run the full test suite:

    pytest server/tests

The current test suite covers:

- Authentication and session handling
- Product creation, retrieval, updates, deletion and stock adjustment
- Sales and sale-item processing
- Transactional inventory updates
- Sale idempotency using client transaction IDs
- Customer creation and purchase history
- Low-stock alert generation, listing and resolution
- Dashboard metrics and daily summaries
- Authentication and validation error cases

There are currently 24 tests across the test modules in `server/tests`.

## Database migrations

Initialize or upgrade the database:

    flask --app server.app db upgrade

Create a new migration after model changes:

    flask --app server.app db migrate -m "describe the change"

The initial schema migration is stored in `migrations/versions/001_initial_retailos.py`.

For a fresh PostgreSQL database, set `DATABASE_URL` before running the migration.

## API areas

The V1 backend currently exposes these main areas:

- `/auth` — registration, login and logout
- `/product` — product and inventory management
- `/customers` — customer management and purchase history
- `/sales` — sales creation, listing, retrieval and receipts
- `/alerts` — low-stock alerts and alert resolution
- `/dashboard` — dashboard metrics and daily business summary

Protected store-level endpoints require an authenticated session and verify that the user has access to the requested store.

## Production

Run the application with Gunicorn:

    gunicorn "server.wsgi:application"

Production configuration expects `SECRET_KEY` and `DATABASE_URL` to be provided through the environment.

The hard-coded development secret was removed. Never commit a real SECRET_KEY or database password.

## Environment

A sample environment configuration is provided in `.env.example`.

For local development, SQLite can be used by leaving `DATABASE_URL` unset. Production deployments should use PostgreSQL.

## Project structure

    server/
        app/
            config.py
            models/
            routes/
            services/
            utils/
        tests/
    migrations/
        versions/
    database/
        schema.sql

Tests use a temporary SQLite database through `TestConfig`, so running the test suite does not require a production database.
