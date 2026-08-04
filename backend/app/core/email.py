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
    <td style="background:linear-gradient(135deg,#312e81 0%,#4f46e5 50%,#6366f1 100%);padding:48px 40px;text-align:center;">
      <!-- Lock icon -->
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto 20px;">
        <tr>
          <td style="background:rgba(255,255,255,0.15);border-radius:50%;width:72px;height:72px;text-align:center;vertical-align:middle;">
            <span style="font-size:36px;line-height:72px;">&#128274;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
        Password Reset Request
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
        We received a request to reset the password associated with
        <strong style="color:#4f46e5;">{to_email}</strong>.
      </p>

      <p style="margin:0 0 28px;color:#4b5563;font-size:15px;line-height:1.7;">
        Click the button below to create a new password. For your security,
        this link will expire in <strong>1 hour</strong>.
      </p>

      <!-- CTA button -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center" style="padding:4px 0 32px;">
            <a href="{reset_link}"
               style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#4338ca);color:#ffffff;padding:16px 40px;border-radius:10px;text-decoration:none;font-weight:600;font-size:15px;letter-spacing:0.3px;box-shadow:0 4px 14px rgba(79,70,229,0.35);">
              Reset Your Password &rarr;
            </a>
          </td>
        </tr>
      </table>

      <!-- Link fallback -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border-radius:10px;margin-bottom:24px;">
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 6px;color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">
              Button not working? Copy this link:
            </p>
            <p style="margin:0;color:#4f46e5;font-size:12px;line-height:1.5;word-break:break-all;">
              {reset_link}
            </p>
          </td>
        </tr>
      </table>

      <!-- Security tips -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;">
        <tr>
          <td style="padding:16px 20px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:32px;vertical-align:top;">
                  <span style="font-size:18px;">&#128272;</span>
                </td>
                <td>
                  <strong style="color:#166534;font-size:13px;">Password Tips</strong>
                  <ul style="margin:6px 0 0;padding-left:16px;color:#15803d;font-size:12px;line-height:1.8;">
                    <li>Use at least 8 characters with a mix of letters, numbers, and symbols</li>
                    <li>Avoid reusing passwords from other services</li>
                    <li>Consider using a password manager for secure storage</li>
                  </ul>
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
        If you didn't request a password reset, you can safely ignore this email.
        Your password will remain unchanged.
      </p>
      <p style="margin:0 0 6px;color:#9ca3af;font-size:12px;">
        This is an automated message from {settings.app_name}.
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
        settings.smtp_sender or settings.smtp_user,
        to_email,
        settings.smtp_host,
        settings.smtp_user,
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


async def send_cofounder_welcome_email(to_email: str, promoted_by_email: str, login_link: str) -> None:
    """Send a premium welcome email when a user is promoted to cofounder."""
    settings = get_settings()

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_sender or settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"{settings.app_name} - Welcome, Cofounder"

    year = __import__("datetime").datetime.now().year

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#1a1a1a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">

<!-- Outer wrapper -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#1a1a1a;padding:40px 0;">
<tr><td align="center">

<!-- Main card -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#1f1f1f;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.4);border:1px solid #333;">

  <!-- Header banner -->
  <tr>
    <td style="background:linear-gradient(135deg,#78520a 0%,#b8860b 40%,#daa520 70%,#b8860b 100%);padding:48px 40px;text-align:center;">
      <!-- Crown icon -->
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto 20px;">
        <tr>
          <td style="background:rgba(0,0,0,0.2);border-radius:50%;width:72px;height:72px;text-align:center;vertical-align:middle;">
            <span style="font-size:36px;line-height:72px;">&#128081;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">
        Welcome, Cofounder
      </h1>
      <p style="margin:0;color:rgba(255,255,255,0.85);font-size:15px;font-weight:400;">
        {settings.app_name}
      </p>
    </td>
  </tr>

  <!-- Body content -->
  <tr>
    <td style="padding:40px;">

      <p style="margin:0 0 20px;color:#e0e0e0;font-size:16px;line-height:1.7;">
        Congratulations! You have been granted <strong style="color:#daa520;">Cofounder</strong>
        privileges on {settings.app_name} by <strong style="color:#e0e0e0;">{promoted_by_email}</strong>.
      </p>

      <p style="margin:0 0 28px;color:#999;font-size:15px;line-height:1.7;">
        As a cofounder, you hold the highest level of authority on the platform.
        Below is an overview of your exclusive capabilities.
      </p>

      <!-- Capabilities grid -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
        <tr>
          <td style="padding:16px 20px;background:#2a2a2a;border-radius:12px 12px 0 0;border-bottom:1px solid #333;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#128101;</span>
                </td>
                <td>
                  <strong style="color:#e0e0e0;font-size:14px;">User Management</strong>
                  <p style="margin:4px 0 0;color:#888;font-size:13px;line-height:1.5;">
                    Full control over all user accounts. Promote and demote admins, manage roles, and oversee platform access.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;background:#2a2a2a;border-bottom:1px solid #333;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#128737;</span>
                </td>
                <td>
                  <strong style="color:#e0e0e0;font-size:14px;">Admin Oversight</strong>
                  <p style="margin:4px 0 0;color:#888;font-size:13px;line-height:1.5;">
                    Only cofounders can grant or revoke admin privileges. Admins cannot modify cofounder accounts.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;background:#2a2a2a;border-bottom:1px solid #333;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#127970;</span>
                </td>
                <td>
                  <strong style="color:#e0e0e0;font-size:14px;">Platform Governance</strong>
                  <p style="margin:4px 0 0;color:#888;font-size:13px;line-height:1.5;">
                    Shape the direction of the platform. Access all projects, buildings, and documents across the system.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;background:#2a2a2a;border-radius:0 0 12px 12px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:40px;vertical-align:top;">
                  <span style="font-size:20px;">&#9881;&#65039;</span>
                </td>
                <td>
                  <strong style="color:#e0e0e0;font-size:14px;">System Configuration</strong>
                  <p style="margin:4px 0 0;color:#888;font-size:13px;line-height:1.5;">
                    Configure platform settings, manage integrations, and maintain system health at the highest level.
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
               style="display:inline-block;background:linear-gradient(135deg,#b8860b,#daa520);color:#1a1a1a;padding:16px 40px;border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;letter-spacing:0.3px;box-shadow:0 4px 14px rgba(218,165,32,0.35);">
              Open Admin Dashboard &rarr;
            </a>
          </td>
        </tr>
      </table>

      <!-- Security notice -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#2a2a00;border:1px solid #4a4a00;border-radius:10px;">
        <tr>
          <td style="padding:16px 20px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:32px;vertical-align:top;">
                  <span style="font-size:18px;">&#128081;</span>
                </td>
                <td>
                  <strong style="color:#daa520;font-size:13px;">Cofounder Privilege</strong>
                  <p style="margin:4px 0 0;color:#b8a000;font-size:12px;line-height:1.5;">
                    With the highest level of access comes the greatest responsibility. Your actions
                    affect all users and administrators on the platform. Exercise your privileges wisely.
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
      <hr style="border:none;border-top:1px solid #333;margin:0;">
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:24px 40px 32px;text-align:center;">
      <p style="margin:0 0 6px;color:#666;font-size:12px;">
        This is an automated message from {settings.app_name}.
      </p>
      <p style="margin:0 0 6px;color:#666;font-size:12px;">
        If you believe this was sent in error, please contact your team lead.
      </p>
      <p style="margin:0;color:#444;font-size:11px;">
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
        "Attempting cofounder welcome email: from=%s to=%s smtp_host=%s smtp_user=%s",
        settings.smtp_sender or settings.smtp_user,
        to_email,
        settings.smtp_host,
        settings.smtp_user,
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
        logger.info("Cofounder welcome email sent to %s, SMTP response: %s", to_email, result)
    except Exception:
        logger.exception("Failed to send cofounder welcome email to %s", to_email)


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
        settings.smtp_sender or settings.smtp_user,
        to_email,
        settings.smtp_host,
        settings.smtp_user,
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
            to_email,
            target_email,
            new_role,
            result,
        )
    except Exception:
        logger.exception("Failed to send demotion confirmation email to %s", to_email)
        raise
