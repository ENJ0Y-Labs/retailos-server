import hmac

import click
from flask import current_app
from sqlalchemy.exc import IntegrityError

from server.app.extensions import db
from server.app.models.platform_audit_log import PlatformAuditLog
from server.app.models.user import PLATFORM_ADMIN_ROLE, User


@click.group(name="platform-admin")
def platform_admin_cli():
    """Controlled platform-administrator provisioning commands."""


@platform_admin_cli.command("bootstrap")
@click.argument("email")
def bootstrap_platform_admin(email):
    """Provision the single first platform administrator.

    The email must match PLATFORM_ADMIN_BOOTSTRAP_EMAIL. The bootstrap token
    is entered interactively and is never accepted as a command-line argument.
    """
    configured_email = current_app.config.get("PLATFORM_ADMIN_BOOTSTRAP_EMAIL")
    expected_token = current_app.config.get("PLATFORM_ADMIN_BOOTSTRAP_TOKEN")

    if not isinstance(configured_email, str) or not configured_email.strip():
        raise click.ClickException("PLATFORM_ADMIN_BOOTSTRAP_EMAIL is not configured")
    if not isinstance(expected_token, str) or len(expected_token) < 32:
        raise click.ClickException(
            "PLATFORM_ADMIN_BOOTSTRAP_TOKEN must be configured with at least 32 characters"
        )

    requested_email = email.strip().lower()
    if requested_email != configured_email.strip().lower():
        raise click.ClickException("The requested email is not the configured bootstrap account")

    supplied_token = click.prompt("Bootstrap token", hide_input=True)
    if not hmac.compare_digest(supplied_token, expected_token):
        raise click.ClickException("Invalid bootstrap token")

    bootstrap_used = PlatformAuditLog.query.filter_by(
        action_type="platform_admin.bootstrap"
    ).first()
    if bootstrap_used:
        raise click.ClickException("The first platform administrator has already been provisioned")

    existing_admin = User.query.filter_by(platform_role=PLATFORM_ADMIN_ROLE).first()
    if existing_admin:
        raise click.ClickException("A platform administrator already exists")

    user = User.query.filter(db.func.lower(User.email) == requested_email).first()
    if not user:
        raise click.ClickException(
            "The configured account must register normally before it can be provisioned"
        )

    user.platform_role = PLATFORM_ADMIN_ROLE
    db.session.add(
        PlatformAuditLog(
            actor_user_id=user.id,
            action_type="platform_admin.bootstrap",
            target_type="user",
            target_id=str(user.id),
            details={"provisioning_method": "restricted_cli"},
        )
    )

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise click.ClickException(
            "Bootstrap was already completed or another provisioning attempt is in progress"
        )

    click.echo("The first platform administrator was provisioned successfully.")
