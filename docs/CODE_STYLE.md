# RetailOS Code Style

## Main rule

Write code that is easy to understand.

Simple and readable code is preferred over clever or compressed code.

## File paths

Start source files with the relative file path.

Example:

    # server/tests/test_auth.py

## Functions

Keep function definitions and their return statements separate.

Prefer:

    def register():
        return auth.register_user()

Do not compress simple functions onto one line.

## Comments

Use simple comments that explain what the code is doing.

Good comments:

    # duplicate email
    # wrong password
    # stale session
    # Check that a customer can be created.

## Formatting

- Keep imports separated clearly.
- Leave blank lines between logical sections.
- Use descriptive variable names.
- Keep related code together.
- Avoid unnecessary abstractions.
- Do not hide important logic inside clever one-liners.

## Tests

Tests should read like a simple story:

1. Set up the data.
2. Perform the action.
3. Check the result.
4. Check important side effects.

Test names should clearly describe what is being checked.

## API and services

Keep route functions small.

Put business logic in services.

Validate input before changing database records.

Check store ownership before reading or changing store data.

## Database transactions

When one business action changes multiple records, keep those changes in one transaction.

If one part fails, roll back the whole action.

## Main project rule

Keep the existing project style consistent.

Readable code is more important than saving a few lines.