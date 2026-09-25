# RetailOS — System Architecture (V1)

## Overview

RetailOS V1 is a Flask-based backend organized around routes, services, models, middleware, and shared utilities.

The architecture is intentionally simple so that the core retail workflows remain easy to understand and maintain.

## 1. Architecture Goals

The backend must provide:

- reliable sales processing
- consistent inventory updates
- store-level authorization
- server-side validation
- safe error responses
- reusable business services
- database migrations
- production PostgreSQL support
- testable application behavior

## 2. High-Level Architecture

The system can be viewed as:

**Client → Flask Routes → Middleware → Services → SQLAlchemy Models/Database**

Supporting components include:

- configuration
- validation utilities
- response utilities
- store authorization
- migrations
- tests

## 3. Application Factory

The application is created through server.app.create_app().

The factory:

- loads configuration
- validates required secrets
- initializes SQLAlchemy
- registers route blueprints
- initializes Flask-Migrate
- registers global error handlers

This keeps application setup separate from individual business services.

## 4. Route Layer

Routes define the HTTP interface and delegate business work to services.

Current route groups:

- /auth
- /product
- /customers
- /sales
- /alerts
- /dashboard

Examples:

- POST /product/create
- GET /product/get
- GET /product/list
- PATCH /product/update
- DELETE /product/delete
- POST /product/adjust
- POST /sales
- GET /sales
- GET /sales/get
- POST /sales/receipt
- GET /customers
- POST /customers
- GET /customers/history
- GET /alerts
- POST /alerts/generate-low-stock
- POST /alerts/resolve
- DELETE /alerts/delete
- GET /dashboard
- GET /dashboard/daily-summary
- GET /dashboard/daily-brief

Protected business endpoints use the session authentication middleware.

## 5. Middleware and Authorization

Authentication is handled through server-side sessions.

Store authorization is checked through a shared authorization utility.

A service should not trust a client-provided store ID by itself. It must verify that the authenticated user is authorized for that store.

This creates a consistent boundary around:

- products
- customers
- sales
- alerts
- dashboard data

## 6. Service Layer

Business logic is kept in service classes.

### ProductService

Responsible for:

- product CRUD
- validation
- stock adjustment
- inventory movement creation

### SalesService

Responsible for:

- sale creation
- sale listing
- sale retrieval
- receipt data
- transaction handling
- inventory reduction
- idempotency

### CustomerService

Responsible for:

- customer creation
- customer listing
- purchase history

### AlertService

Responsible for:

- low-stock alert generation
- alert listing
- alert resolution

### InsightService

Responsible for:

- dashboard metrics
- daily summary
- daily business brief
- sales comparison
- restock recommendations
- top product insight

## 7. Validation

Validation is performed before business operations are committed.

Examples include:

- required strings
- non-negative prices
- valid integer quantities
- valid store IDs
- valid product/customer references

The API returns structured validation errors instead of allowing malformed input to reach deeper database operations.

## 8. Sales Transaction Flow

A sale follows this sequence:

1. route receives request
2. authentication middleware verifies session
3. service validates input
4. store access is verified
5. customer and products are checked
6. product inventory is read with transactional protection
7. stock availability is checked
8. server calculates item totals
9. server calculates the sale total
10. sale is created
11. sale items are created
12. inventory is reduced
13. inventory movements are created
14. transaction commits
15. receipt data is returned

If processing fails, the database transaction is rolled back.

## 9. Idempotency

Sales accept an optional client_transaction_id.

The database keeps this identifier unique.

The service checks for an existing transaction before processing a new sale.

This prevents a client retry from creating a second sale and reducing inventory twice.

## 10. Database Layer

SQLAlchemy provides the application database interface.

Development and tests can use SQLite.

Production is configured for PostgreSQL through DATABASE_URL.

Flask-Migrate manages schema migrations.

The initial migration is:

migrations/versions/001_initial_retailos.py

## 11. Error Handling

Global Flask handlers cover common failures such as:

- bad requests
- missing routes
- unsupported methods
- database integrity conflicts
- unexpected server exceptions

Internal exception details are logged server-side but are not returned to API clients.

## 12. Production Runtime

The production WSGI entry point is server/wsgi.py.

Gunicorn runs:

gunicorn "server.wsgi:application"

Production configuration expects:

- SECRET_KEY
- DATABASE_URL

These values must be supplied through the deployment environment rather than committed to source control.

## 13. Testing Architecture

Tests use TestConfig and an in-memory SQLite database.

The test fixture:

1. creates the Flask application
2. creates database tables
3. runs the test
4. removes the session
5. drops the test tables

Current test modules cover:

- authentication
- products
- sales
- customers
- alerts
- dashboard

## 14. Security Principles

- authentication is required for protected operations
- passwords are hashed
- store access is verified server-side
- production secrets are environment-based
- internal exceptions are not exposed
- database integrity constraints protect important values

## 15. Future Architecture

The current modular structure leaves room for:

- more alert rules
- richer insights
- payments
- suppliers
- audit logging
- multi-store access
- external integrations
- background jobs
- analytics

These should be added without weakening the core transaction and authorization boundaries.

## Final Summary

RetailOS V1 is a modular Flask backend where:

**Routes handle HTTP → middleware handles authentication → services handle business rules → models handle persistence → transactions protect business integrity.**
