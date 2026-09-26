import importlib.util
from pathlib import Path


MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "versions"
    / "003_model_constraints.py"
)


class OperationRecorder:
    def __init__(self):
        self.created_constraints = []
        self.dropped_constraints = []
        self.executed = []

    def create_check_constraint(self, name, table_name, condition):
        self.created_constraints.append((name, table_name, condition))

    def drop_constraint(self, name, table_name, type_):
        self.dropped_constraints.append((name, table_name, type_))

    def execute(self, statement):
        self.executed.append(str(statement))


def load_migration():
    spec = importlib.util.spec_from_file_location(
        "migration_003_model_constraints",
        MIGRATION_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Check that every check constraint created by migration 003 can be downgraded.
def test_model_constraint_migration_is_reversible():
    migration = load_migration()
    recorder = OperationRecorder()
    migration.op = recorder

    migration.upgrade()
    migration.downgrade()

    created_names = [item[0] for item in recorder.created_constraints]
    dropped_names = [item[0] for item in recorder.dropped_constraints]

    assert set(created_names) == set(dropped_names)
    assert "check_price_non_negative" in created_names
    assert "check_stock_quantity_non_negative" in created_names
    assert "check_product_price_non_negative" not in dropped_names
    assert "check_product_stock_non_negative" not in dropped_names
    assert any("DROP INDEX IF EXISTS uq_users_email_lower" in statement for statement in recorder.executed)
