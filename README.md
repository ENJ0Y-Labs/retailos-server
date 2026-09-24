# RetailOS Server

RetailOS is a Flask backend for retail product, inventory, sales and customer management.

## Development

Set a secret before starting the application:

    export SECRET_KEY="your-secret"

For PostgreSQL:

    export DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/retailos"

Install dependencies:

    pip install -r server/requirements.txt

Run tests:

    pytest server/tests

Run migrations:

    flask --app server.app db upgrade

Production:

    gunicorn --chdir server "app:application"

The hard-coded development secret was removed. Never commit a real SECRET_KEY or database password.
