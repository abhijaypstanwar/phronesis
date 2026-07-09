import smtplib, random, string
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
    html = f"""<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f8f8f8;border-radius:12px;">
        <h1 style="color:#0a0a0a;font-size:22px;">Phronesis</h1>
        <p style="color:#888;font-size:12px;">φρόνησις — Practical Wisdom</p>
        <div style="background:#fff;border-radius:10px;padding:28px;border:1px solid #e5e5e5;margin-top:16px;">
            <p style="color:#444;">Hi <strong>{name}</strong>,</p>
            <p style="color:#444;">Your verification code:</p>
            <div style="text-align:center;margin:24px 0;">
                <span style="font-size:40px;font-weight:700;letter-spacing:12px;color:#6c63ff;">{otp}</span>
            </div>
            <p style="color:#888;font-size:12px;">Expires in 10 minutes. If you didn't request this, ignore this email.</p>
        </div>
    </div>"""
    send_email(to, "Your Phronesis verification code", html)

def send_reset_email(to: str, name: str, reset_token: str):
    reset_url = f"http://localhost:8000/reset?token={reset_token}"
    html = f"""<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f8f8f8;border-radius:12px;">
        <h1 style="color:#0a0a0a;font-size:22px;">Phronesis</h1>
        <div style="background:#fff;border-radius:10px;padding:28px;border:1px solid #e5e5e5;margin-top:16px;">
            <p style="color:#444;">Hi <strong>{name}</strong>,</p>
            <p style="color:#444;">Click below to reset your password. Link expires in 15 minutes.</p>
            <div style="text-align:center;margin:24px 0;">
                <a href="{reset_url}" style="background:#6c63ff;color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;">Reset my password</a>
            </div>
            <p style="color:#888;font-size:12px;">Or paste: {reset_url}</p>
        </div>
    </div>"""
    send_email(to, "Reset your Phronesis password", html)
