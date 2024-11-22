# # app/email_utils.py

# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# FROM_EMAIL = 'your_email@example.com'  # Replace with your verified sender email

# def send_confirmation_email(to_email, subject, content):
#     message = Mail(
#         from_email=FROM_EMAIL,
#         to_emails=to_email,
#         subject=subject,
#         html_content=content)
#     try:
#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)
#         print(f"Email sent to {to_email}: {response.status_code}")
#     except Exception as e:
#         print(f"Error sending email to {to_email}: {e}")
