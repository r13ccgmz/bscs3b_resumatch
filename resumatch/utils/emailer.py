import smtplib
from email.mime.text import MIMEText

def send_email(recipient_email, accepted):
    sender_email = 'aldridge2425@gmail.com'
    sender_password = 'aelumacas25'

    if accepted:
        subject = 'Invitation for Interview - Company Name'
        body = 'Dear Applicant,\n\nWe are pleased to invite you for an interview...'
    else:
        subject = 'Application Update - Company Name'
        body = 'Dear Applicant,\n\nThank you for your interest. Unfortunately...'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the email via SMTP server
    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f'Failed to send email: {e}')