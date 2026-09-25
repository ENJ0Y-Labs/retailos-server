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

The test suite covers:

- Authentication and session handling
- Production configuration requirements
- Product creation, retrieval, updates and deletion
- Product validation and store authorization
- Stock adjustment and negative-stock protection
- Inventory movement history
- Sales and sale-item processing
- Transactional inventory updates and rollback
- Sale idempotency using client transaction IDs
- Receipt data and printable receipt text
- Customer creation and purchase history
- Customer validation and store authorization
- Low-stock alert generation, listing and resolution
- Alert store authorization
- Dashboard metrics and daily summaries

## Database migrations

Initialize or upgrade the database:

    flask --app server.app db upgrade

Create a new migration after model changes:

    flask --app server.app db migrate -m "describe the change"

The initial schema migration is stored in migrations/versions/001_initial_retailos.py.

The V1 alert scope migration is stored in migrations/versions/002_v1_alert_scope.py.

For a fresh PostgreSQL database, set DATABASE_URL before running the migration.

## API areas

The V1 backend currently exposes these main areas:

- /auth — registration, login and logout
- /product — product and inventory management
- /product/movements — inventory movement history
- /customers — customer management and purchase history
- /sales — sales creation, listing, retrieval and receipts
- /alerts — low-stock alerts and alert resolution
- /dashboard — dashboard metrics and daily business summary

Protected store-level endpoints require an authenticated session and verify that the user has access to the requested store.

## V1 alert scope

V1 currently implements low-stock alerts.

Sales-drop and no-sales alerts are not part of the current V1 behavior. They can be added later as separate features instead of exposing enum values for features that are not implemented.

## Receipts

The receipt endpoint returns structured receipt data and printable receipt text.

It does not claim to generate a PDF. A PDF or printer-specific format can be added later without changing the sale transaction logic.

## Production

Run the application with Gunicorn:

    gunicorn "server.wsgi:application"

Production configuration requires:

- SECRET_KEY
- DATABASE_URL

The application refuses to start with ProductionConfig when either required value is missing.

The hard-coded development secret was removed.

Because the old secret was previously committed, generate and install a new production SECRET_KEY before deployment. See docs/SECURITY.md.

Never commit a real SECRET_KEY or database password.

## Environment

A sample environment configuration is provided in .env.example.

For local development, SQLite can be used by leaving DATABASE_URL unset.

Production deployments should use PostgreSQL.

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
    docs/

Tests use a temporary SQLite database through TestConfig, so running the test suite does not require a production database.