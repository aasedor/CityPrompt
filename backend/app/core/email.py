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
