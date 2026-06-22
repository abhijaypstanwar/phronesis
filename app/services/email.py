import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def send_email(to: str, subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.MAIL_FROM
    msg["To"]      = to
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(settings.MAIL_FROM, to, msg.as_string())


def send_otp_email(to: str, name: str, otp: str):
    subject = "Your Phronesis verification code"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f8f8f8;border-radius:12px;">
        <div style="text-align:center;margin-bottom:24px;">
            <h1 style="color:#0a0a0a;font-size:24px;margin:0;">Phronesis</h1>
            <p style="color:#888;font-size:13px;margin:4px 0 0;">φρόνησις — Practical Wisdom</p>
        </div>
        <div style="background:#fff;border-radius:10px;padding:28px;border:1px solid #e5e5e5;">
            <p style="color:#444;font-size:15px;margin:0 0 16px;">Hi <strong>{name}</strong>,</p>
            <p style="color:#444;font-size:14px;margin:0 0 24px;line-height:1.6;">
                Use the code below to verify your account. This code expires in <strong>10 minutes</strong>.
            </p>
            <div style="text-align:center;margin:24px 0;">
                <span style="font-size:40px;font-weight:700;letter-spacing:12px;color:#6c63ff;">{otp}</span>
            </div>
            <p style="color:#888;font-size:12px;margin:24px 0 0;text-align:center;">
                If you didn't request this, you can safely ignore this email.
            </p>
        </div>
        <p style="color:#bbb;font-size:11px;text-align:center;margin-top:20px;">© 2026 Phronesis. All rights reserved.</p>
    </div>
    """
    send_email(to, subject, html)


def send_reset_email(to: str, name: str, reset_token: str):
    reset_url = f"http://localhost:8000/reset?token={reset_token}"
    subject   = "Reset your Phronesis password"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f8f8f8;border-radius:12px;">
        <div style="text-align:center;margin-bottom:24px;">
            <h1 style="color:#0a0a0a;font-size:24px;margin:0;">Phronesis</h1>
            <p style="color:#888;font-size:13px;margin:4px 0 0;">φρόνησις — Practical Wisdom</p>
        </div>
        <div style="background:#fff;border-radius:10px;padding:28px;border:1px solid #e5e5e5;">
            <p style="color:#444;font-size:15px;margin:0 0 16px;">Hi <strong>{name}</strong>,</p>
            <p style="color:#444;font-size:14px;margin:0 0 24px;line-height:1.6;">
                Click the button below to reset your password. This link expires in <strong>15 minutes</strong>.
            </p>
            <div style="text-align:center;margin:24px 0;">
                <a href="{reset_url}" style="background:#6c63ff;color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;">Reset my password</a>
            </div>
            <p style="color:#888;font-size:12px;margin:24px 0 0;">
                Or paste this link: <span style="color:#6c63ff;">{reset_url}</span>
            </p>
        </div>
        <p style="color:#bbb;font-size:11px;text-align:center;margin-top:20px;">© 2026 Phronesis. All rights reserved.</p>
    </div>
    """
    send_email(to, subject, html)
