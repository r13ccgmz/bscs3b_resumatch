# emailer.py
import smtplib
from email.mime.text import MIMEText

def send_email(recipient_email, accepted, qualification_grade, skills_score, education_score, experience_score, applicant_name):
    sender_email = 'HR.AutoEmailer@gmail.com'
    sender_password = 'pvpo ysnj xsed lhmc'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    if accepted:
        subject = 'Invitation for Interview - IQuiryJS'
        body = (f"Dear {applicant_name},\n\n"
    f"We are pleased to invite you for an interview.\n\n"
    f"Your Scores:\n"
    f"Qualification Grade: {qualification_grade:.2f}\n"
    f"Skills Score: {skills_score:.2f}\n"
    f"Education Score: {education_score:.2f}\n"
    f"Experience Score: {experience_score:.2f}\n\n"
    f"Best regards,\nCompany HR Team")
    
    else:
        subject = 'Application Update - IQuiryJS'
        body = (f"Dear {applicant_name},\n\n"
        "Thank you for applying.\n"
    f"After careful consideration, we regret to inform you that we will not be moving forward with your application.\n\n"
    f"Your Scores:\n"
    f"Qualification Grade: {qualification_grade:.2f}\n"
    f"Skills Score: {skills_score:.2f}\n"
    f"Education Score: {education_score:.2f}\n"
    f"Experience Score: {experience_score:.2f}\n\n"
    f"Best regards,\nCompany HR Team")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the email via SMTP server
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f'Failed to send email to {recipient_email}: {e}')