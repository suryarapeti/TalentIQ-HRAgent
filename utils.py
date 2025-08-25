import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email(to_email, subject, body):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print(f"Error: Email credentials not configured. Missing: {', '.join([var for var, val in [('EMAIL_SENDER', sender_email), ('SMTP_PASSWORD', sender_password)] if not val])}")
        return False
    
    if not to_email or not to_email.strip():
        print("Error: Recipient email address is empty or invalid")
        return False
    
    receiver_email = to_email.strip()
    
    # SMTP server configuration
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.getenv("SMTP_PORT", "587")
    
    try:
        smtp_port = int(smtp_port_str)
    except (ValueError, TypeError):
        print(f"Error: Invalid SMTP_PORT value: {smtp_port_str}. Using default 587.")
        smtp_port = 587
    
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
    except Exception as e:
        print(f"Error creating email message: {e}")
        return False
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication failed: {e}")
        print("Please check your EMAIL_SENDER and SMTP_PASSWORD credentials")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
