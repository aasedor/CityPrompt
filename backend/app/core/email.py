"""
Async SMTP email sender for password reset emails.
Uses aiosmtplib with Gmail STARTTLS.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def send_password_reset_email(to_email: str, reset_link: str) -> None:
    """Send a password reset email with the given reset link."""
    settings = get_settings()

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_sender or settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"{settings.app_name} - Password Reset"

    html = f"""\
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
  <h2 style="color: #1a1a1a;">Password Reset</h2>
  <p style="color: #4a4a4a; line-height: 1.6;">
    You requested a password reset for your {settings.app_name} account.
    Click the button below to set a new password. This link expires in 1 hour.
  </p>
  <a href="{reset_link}"
     style="display: inline-block; background: #4f46e5; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 16px 0;">
    Reset Password
  </a>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">
    If you didn't request this, you can safely ignore this email.
  </p>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Password reset email sent to %s", to_email)
    except Exception:
        logger.exception("Failed to send password reset email to %s", to_email)
        raise


async def send_admin_welcome_email(to_email: str, promoted_by_email: str, login_link: str) -> None:
    """Send a congratulations email when a user is promoted to admin."""
    settings = get_settings()

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_sender or settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"{settings.app_name} - Welcome to the Admin Team!"

    html = f"""\
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
  <h2 style="color: #1a1a1a;">Welcome, Admin!</h2>
  <p style="color: #4a4a4a; line-height: 1.6;">
    Congratulations! <strong>{promoted_by_email}</strong> has granted you
    <strong>admin</strong> access on {settings.app_name}.
  </p>
  <p style="color: #4a4a4a; line-height: 1.6;">
    As an admin you can now manage users, oversee all projects, and
    configure platform settings.
  </p>
  <a href="{login_link}"
     style="display: inline-block; background: #16a34a; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 16px 0;">
    Go to Admin Dashboard
  </a>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">
    If you believe this was a mistake, please contact your team lead.
  </p>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))

    logger.info(
        "Attempting admin welcome email: from=%s to=%s smtp_host=%s smtp_user=%s",
        settings.smtp_sender or settings.smtp_user, to_email, settings.smtp_host, settings.smtp_user,
    )
    try:
        result = await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Admin welcome email sent to %s, SMTP response: %s", to_email, result)
    except Exception:
        logger.exception("Failed to send admin welcome email to %s", to_email)


async def send_admin_demotion_confirmation_email(
    to_email: str,
    target_email: str,
    new_role: str,
    confirm_link: str,
) -> None:
    """Send a confirmation email when an admin demotes another admin."""
    settings = get_settings()

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_sender or settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"{settings.app_name} - Confirm Role Change"

    html = f"""\
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
  <h2 style="color: #1a1a1a;">Confirm Role Change</h2>
  <p style="color: #4a4a4a; line-height: 1.6;">
    You requested to change <strong>{target_email}</strong>'s role from
    <strong>admin</strong> to <strong>{new_role}</strong> on {settings.app_name}.
  </p>
  <p style="color: #4a4a4a; line-height: 1.6;">
    This will revoke their admin privileges. Click the button below to confirm
    this change. This link expires in 1 hour.
  </p>
  <a href="{confirm_link}"
     style="display: inline-block; background: #dc2626; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 16px 0;">
    Confirm Role Change
  </a>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">
    If you didn't request this change, you can safely ignore this email.
  </p>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))

    logger.info(
        "Attempting demotion confirmation email: from=%s to=%s smtp_host=%s smtp_user=%s",
        settings.smtp_sender or settings.smtp_user, to_email, settings.smtp_host, settings.smtp_user,
    )
    try:
        result = await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info(
            "Admin demotion confirmation email sent to %s (target: %s -> %s), SMTP response: %s",
            to_email, target_email, new_role, result,
        )
    except Exception:
        logger.exception("Failed to send demotion confirmation email to %s", to_email)
        raise
