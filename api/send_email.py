import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv(override=True)
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)


def send_email(
    subject,
    body,
    to_email,
    from_email,
    password,
    smtp_server,
    smtp_port=465,
    attachments=None  # List of file paths
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)

    # Add attachments if any
    if attachments:
        for file_path in attachments:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = f.name.split("/")[-1]
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    # Secure connection and send
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(from_email, password)
        server.send_message(msg)

    print("Email sent successfully.")


send_email(
    subject="new key",
    body="Here is my CV .",
    to_email="torm8078@gmail.com",
    from_email="tony.rmaili@gmail.com",
    password=os.getenv("GMAIL_APP_PASSWORD"),  # Use an app password, not your regular one!
    smtp_server="smtp.gmail.com"  
)
