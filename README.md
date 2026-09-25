# RetailOS Server

Flask API backend for RetailOS.

## Development

Set:

    export SECRET_KEY="your-secret"
    export FRONTEND_URL="http://localhost:3000"
    export SESSION_COOKIE_SECURE="false"
    export SESSION_COOKIE_SAMESITE="Lax"

For PostgreSQL:

    export DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/retailos"

Install:

    pip install -r server/requirements.txt

Run tests:

    pytest server/tests

Run migrations:

    flask --app server.app db upgrade

Production:

    FRONTEND_URL="https://your-client.example"
    SESSION_COOKIE_SECURE="true"
    SESSION_COOKIE_SAMESITE="None"
    gunicorn "server.wsgi:application"

The frontend uses credentialed cross-origin requests and the Flask HttpOnly session cookie. The API therefore allowlists the exact FRONTEND_URL rather than using a wildcard CORS origin. For production, serve both applications over HTTPS and keep SECRET_KEY private.

The current API contract covers authentication, stores, products, inventory adjustments, sales, customers, alerts and dashboard insights.
