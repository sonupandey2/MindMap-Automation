import os
import requests

def send_email():

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Automation Notification</title>
    </head>

    <body style="margin:0; padding:0; background-color:#f4f6f8;
                 font-family:Arial, Helvetica, sans-serif;">

        <table width="100%" cellpadding="0" cellspacing="0"
               style="background-color:#f4f6f8; padding:40px 20px;">

            <tr>
                <td align="center">

                    <table width="600" cellpadding="0" cellspacing="0"
                           style="max-width:600px; background:#ffffff;
                                  border-radius:10px; overflow:hidden;
                                  box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                        <!-- Header -->
                        <tr>
                            <td style="background:#1f4e78; padding:25px 35px;
                                       color:#ffffff;">

                                <h1 style="margin:0; font-size:24px;">
                                    Automation Notification
                                </h1>

                                <p style="margin:8px 0 0;
                                          font-size:14px; opacity:0.9;">
                                    Mailgun Email Service
                                </p>

                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding:35px; color:#333333;">

                                <h2 style="margin-top:0;
                                           font-size:22px;">
                                    Hello Sonu Pandey 👋
                                </h2>

                                <p style="font-size:16px; line-height:1.6;">
                                    Congratulations! Your email automation
                                    has been executed successfully.
                                </p>

                                <!-- Status Box -->
                                <table width="100%" cellpadding="0"
                                       cellspacing="0"
                                       style="margin:25px 0;
                                              background:#f0f8f4;
                                              border-left:4px solid #28a745;">

                                    <tr>
                                        <td style="padding:15px 18px;">

                                            <strong style="color:#218838;">
                                                ✓ Automation Successful
                                            </strong>

                                            <p style="margin:8px 0 0;
                                                      color:#555555;
                                                      font-size:14px;">
                                                Your email was successfully
                                                delivered through Mailgun.
                                            </p>

                                        </td>
                                    </tr>

                                </table>

                                <p style="font-size:15px; line-height:1.6;">
                                    This email was generated automatically
                                    by your automation workflow.
                                </p>

                                <p style="font-size:15px; line-height:1.6;">
                                    You can now continue building and
                                    automating your workflow with confidence.
                                </p>

                                <p style="margin-top:30px;
                                          font-size:15px;">
                                    Regards,<br>
                                    <strong>Automation System</strong>
                                </p>

                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background:#f8f9fa;
                                       padding:20px 35px;
                                       text-align:center;
                                       color:#777777;
                                       font-size:12px;">

                                <p style="margin:0;">
                                    This is an automated message.
                                    Please do not reply to this email.
                                </p>

                                <p style="margin:8px 0 0;">
                                    © 2026 Automation System
                                </p>

                            </td>
                        </tr>

                    </table>

                </td>
            </tr>

        </table>

    </body>
    </html>
    """

    api_key = os.environ.get("MAILGUN_API_KEY", "your-mailgun-api-key")
    response = requests.post(
        "https://api.mailgun.net/v3/sandboxed630cd93ad341caaaa62af31fd9c371.mailgun.org/messages",

        auth=("api", api_key),

        data={
            "from": "Automation System <postmaster@sandboxed630cd93ad341caaaa62af31fd9c371.mailgun.org>",
            "to": "Sonu Pandey <sonupandey6061@gmail.com>",
            "subject": "Automation Successful – Email Delivery Confirmation",
            "text": "Hello Sonu Pandey, your email automation was successfully executed.",
            "html": html_content
        }
    )

    print(response.status_code)
    print(response.text)


send_email()