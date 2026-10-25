import smtplib
import os

from email.message import EmailMessage
from getpass import getpass


# Gmail account details
sender_email = "mindmap.automation@gmail.com"
receiver_email = "sonupandey6061@gmail.com"

# Gmail App Password via environment variable
app_password = os.environ.get("GMAIL_APP_PASSWORD", "your-app-password")


# Create the email
message = EmailMessage()

message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Test Email Using Python"

message.set_content("""
Hello,

This is a test email sent using Python
from my personal Gmail account.

Regards
""")


try:
    # Connect to Gmail SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(sender_email, app_password)

        server.send_message(message)

    print("Email sent successfully!")

except Exception as error:
    print("Failed to send email:", error)