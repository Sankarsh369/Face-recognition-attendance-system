import smtplib
import os
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_attendance_email(student_name, reg_no, status, date):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    if not sender_email or not sender_password:
        return "Email credentials not set."

    parent_emails = {}

    try:
        with open("data/students.csv", "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if "Reg No" in row and "Parent Email" in row:
                    parent_emails[row["Reg No"].strip()] = row["Parent Email"].strip()  

    except FileNotFoundError:
        return "Error: students.csv not found."
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

    parent_email = parent_emails.get(reg_no.strip())
    if not parent_email:
        return f"No email found for student {student_name} (Reg No: {reg_no})"

    student_name = student_name.capitalize()

    subject = f"Attendance Update for {date}"
    body = f"Dear Parent,\n\nYour ward {student_name} (Reg No: {reg_no}) is marked as {status} today ({date}).\n\nRegards,\nSchool Administration"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = parent_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, parent_email, msg.as_string())
        print(f"Email sent to {parent_email}")
        return f"Email sent to {parent_email}"
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return f"Failed to send email: {str(e)}"