# database/seed.py
import os
import sys

from sqlalchemy import create_engine, text


def seed_database(database_url, seed_sql_path):
    engine = create_engine(database_url)

    with open(seed_sql_path, "rt", encoding="utf-8") as seed_sql:
        seed = seed_sql.read()

    with engine.begin() as connection:
        for statement in seed.split(";"):
            statement = statement.strip()

            if statement:
                connection.execute(text(statement))

    print("Seeded Successfully")


if __name__ == "__main__":
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        print("DATABASE_URL must be configured before seeding", file=sys.stderr)
        raise SystemExit(1)

    seed_database(
        database_url,
        "database/seed.sql"
    )
