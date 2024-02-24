import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Set up logging configuration
logging.basicConfig(filename='email.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def send_email(receiver_email, subject, body):
    # Check if sender_email is a string
    sender_email = "gokul465eswaran@gmail.com"
    sender_password = "atmzhywjibkcmbal"
    if not isinstance(sender_email, str):
        logging.error("Sender email is not a string")
        return

    # Check if receiver_email is a string
    if not isinstance(receiver_email, str):
        logging.error("Receiver email is not a string")
        return

    # Check if subject is a string
    if not isinstance(subject, str):
        logging.error("Subject is not a string")
        return

    # Check if body is a string
    if not isinstance(body, str):
        logging.error("Body is not a string")
        return

    # Your email credentials
    
    

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach body to the email
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")

    # Log when the function has finished executing
    logging.info("send_email function finished execution")

# Example usage:
# send_email('recipient@example.com', 'Match Found', 'A match has been found for your submitted case.')
