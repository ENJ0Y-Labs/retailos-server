import importlib.util
from pathlib import Path


MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "versions"
    / "004_sale_timestamp_utc.py"
)


class OperationRecorder:
    def __init__(self):
        self.executed = []

    def execute(self, statement):
        self.executed.append(str(statement))


def load_migration():
    spec = importlib.util.spec_from_file_location(
        "migration_004_sale_timestamp_utc",
        MIGRATION_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sale_timestamp_migration_converts_existing_values_to_utc_and_corrects_future_rows():
    migration = load_migration()
    recorder = OperationRecorder()
    migration.op = recorder

    migration.upgrade()

    assert any("TYPE TIMESTAMPTZ" in statement for statement in recorder.executed)
    assert any(
        "USING created_at AT TIME ZONE 'UTC'" in statement
        for statement in recorder.executed
    )
    assert any(
        "SET created_at = CURRENT_TIMESTAMP" in statement
        and "WHERE created_at > CURRENT_TIMESTAMP" in statement
        for statement in recorder.executed
    )


def test_sale_timestamp_migration_downgrade_returns_to_timezone_naive_timestamp():
    migration = load_migration()
    recorder = OperationRecorder()
    migration.op = recorder

    migration.downgrade()

    assert any("TYPE TIMESTAMP" in statement for statement in recorder.executed)
