# RetailOS Code Style

## 1. Put the file path at the top

Every source file should start with its relative path.

Example:

# server/tests/test_auth.py

This makes it easy to know where the code belongs when it is copied, reviewed, or discussed.

## 2. Keep the code simple

Write code in a way that is easy to read and easy to explain.

Prefer:

def register():
    return auth.register_user()

Instead of:

def register(): return auth.register_user()

## 3. Keep function definitions and returns separate

Use normal line breaks for function bodies.

Prefer:

def get_product():
    product = find_product()

    return product

Avoid putting the whole function on one line.

## 4. Use simple comments

Comments should explain what the code is doing in normal, simple language.

Good:

# Check if the user owns this store.

Avoid comments that use complicated technical language when a simple explanation is enough.

## 5. Comment the important parts

Comments are useful for:

- authentication checks
- database transactions
- inventory changes
- validation
- cleanup in tests
- code that may not be obvious later

Do not comment every single line when the code already explains itself.

## 6. Keep related code together

Keep imports at the top, followed by classes and functions.

Keep related tests together.

Keep related business logic inside the service that owns it.

## 7. Keep tests easy to follow

A test should read like a simple story:

1. Set up the data.
2. Perform the action.
3. Check the result.
4. Clean up when needed.

Use simple test names that describe what is being checked.

Example:

def test_create_product(client):
    ...

## 8. Do not hide important logic

Avoid unnecessary one-line statements when they make the code harder to understand.

Prefer readable blocks over compressed code.

## 9. Preserve the existing project style

When adding or changing code, follow the style already used by the project instead of introducing a different formatting style.

## 10. Main rule

The code should be understandable by the person who wrote it and by the person who has to maintain it later.

Simple, readable, and clear is preferred over clever or compressed code.
