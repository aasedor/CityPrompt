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

    year = __import__("datetime").datetime.now().year

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">

<!-- Outer wrapper -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f2f5;padding:40px 0;">
<tr><td align="center">

<!-- Main card -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

  <!-- Header banner -->
  <tr>
    <td style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 50%,#3b82f6 100%);padding:48px 40px;text-align:center;">
      <!-- Shield icon -->
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto 20px;">
        <tr>
          <td style="background:rgba(255,255,255,0.15);border-radius:50%;width:72px;height:72px;text-align:center;vertical-align:middle;">
            <span style="font-size:36px;line-height:72px;">&#128737;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
        Welcome to the Admin Team
      </h1>
      <p style="margin:0;color:rgba(255,255,255,0.85);font-size:15px;font-weight:400;">
        {settings.app_name}
      </p>
    </td>
  </tr>

  <!-- Body content -->
  <tr>
    <td style="padding:40px;">

      <p style="margin:0 0 20px;color:#1a1a1a;font-size:16px;line-height:1.7;">
        Congratulations! You have been granted <strong style="color:#2563eb;">Administrator</strong>
        privileges on {settings.app_name} by <strong>{promoted_by_email}</strong>.
      </p>

      <p style="margin:0 0 28px;color:#4b5563;font-size:15px;line-height:1.7;">
        As an administrator, you now have elevated access to help manage and grow our platform.
        Below is an overview of your new capabilities.
      </p>

      <!-- Capabilities grid -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
        <tr>
          <td style="padding:16px 20px;background:#f8fafc;border-radius:12px 12px 0 0;border-bottom:1px solid #e5e7eb;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#128101;</span>
                </td>
                <td>
                  <strong style="color:#1a1a1a;font-size:14px;">User Management</strong>
                  <p style="margin:4px 0 0;color:#6b7280;font-size:13px;line-height:1.5;">
                    Add, remove, and manage user accounts. Assign roles and control access levels across the platform.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;background:#f8fafc;border-bottom:1px solid #e5e7eb;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#128203;</span>
                </td>
                <td>
                  <strong style="color:#1a1a1a;font-size:14px;">Project Oversight</strong>
                  <p style="margin:4px 0 0;color:#6b7280;font-size:13px;line-height:1.5;">
                    View and manage all projects across the platform. Monitor progress, review submissions, and ensure quality standards.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;background:#f8fafc;border-bottom:1px solid #e5e7eb;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#128202;</span>
                </td>
                <td>
                  <strong style="color:#1a1a1a;font-size:14px;">Platform Analytics</strong>
                  <p style="margin:4px 0 0;color:#6b7280;font-size:13px;line-height:1.5;">
                    Access the admin dashboard with real-time statistics on users, projects, buildings, and platform activity.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;background:#f8fafc;border-radius:0 0 12px 12px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#9881;&#65039;</span>
                </td>
                <td>
                  <strong style="color:#1a1a1a;font-size:14px;">Platform Configuration</strong>
                  <p style="margin:4px 0 0;color:#6b7280;font-size:13px;line-height:1.5;">
                    Configure platform settings, manage integrations, and maintain system health to keep everything running smoothly.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>

      <!-- CTA button -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center" style="padding:4px 0 32px;">
            <a href="{login_link}"
               style="display:inline-block;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;padding:16px 40px;border-radius:10px;text-decoration:none;font-weight:600;font-size:15px;letter-spacing:0.3px;box-shadow:0 4px 14px rgba(37,99,235,0.35);">
              Open Admin Dashboard &rarr;
            </a>
          </td>
        </tr>
      </table>

      <!-- Security notice -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;">
        <tr>
          <td style="padding:16px 20px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:32px;vertical-align:top;">
                  <span style="font-size:18px;">&#9888;&#65039;</span>
                </td>
                <td>
                  <strong style="color:#92400e;font-size:13px;">Security Reminder</strong>
                  <p style="margin:4px 0 0;color:#a16207;font-size:12px;line-height:1.5;">
                    With admin access comes great responsibility. Never share your credentials,
                    always verify before modifying user accounts, and report any suspicious activity immediately.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>

    </td>
  </tr>

  <!-- Divider -->
  <tr>
    <td style="padding:0 40px;">
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:0;">
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:24px 40px 32px;text-align:center;">
      <p style="margin:0 0 6px;color:#9ca3af;font-size:12px;">
        This is an automated message from {settings.app_name}.
      </p>
      <p style="margin:0 0 6px;color:#9ca3af;font-size:12px;">
        If you believe this was sent in error, please contact your team lead.
      </p>
      <p style="margin:0;color:#d1d5db;font-size:11px;">
        &copy; {year} {settings.app_name}. All rights reserved.
      </p>
    </td>
  </tr>

</table>
<!-- /Main card -->

</td></tr>
</table>
<!-- /Outer wrapper -->

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
