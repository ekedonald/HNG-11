import os
from dotenv import load_dotenv
from flask import Flask, request
from celery import Celery
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from logging.handlers import RotatingFileHandler
import logging

load_dotenv()

# Create and configure the Flask app
app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configure logging
log_file = '/var/log/messaging_system.log'
handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@celery.task
def send_email(recipient):
    sender = "eke.ikenna71@gmail.com"
    password = os.environ.get('EMAIL_PASSWORD')
    msg = MIMEText("This is a test email sent from Eke-Donald to test the Messaging System with RabbitMQ/Celery and Python Application behind Nginx.")
    msg['Subject'] = "Eke-Donald HNG11 DevOps Engineer"
    msg['From'] = sender
    msg['To'] = recipient
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipient, msg.as_string())
        app.logger.info(f"Email sent successfully to {recipient}")
        return "Email sent successfully"
    except Exception as e:
        error_message = f"Error sending email to {recipient}: {str(e)}"
        app.logger.error(error_message)
        return error_message

@app.route('/')
def index():
    if 'sendmail' in request.args:
        recipient = request.args.get('sendmail')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app.logger.info(f"Sendmail request received for {recipient} at {current_time}")
        send_email.delay(recipient)
        return f"Email sending task queued for {recipient}"
    
    elif 'talktome' in request.args:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app.logger.info(f"Talktome request received at {current_time}")
        return f"Request logged at {current_time}"
    
    else:
        return "Welcome to the messaging system. Use ?sendmail or ?talktome parameters."

@app.route('/logs')
def view_logs():
    log_file_path = '/var/log/messaging_system.log'
    if os.path.exists(log_file_path):
        app.logger.info(f"Log file accessed at {datetime.now()}")
        return send_file(log_file_path, mimetype='text/plain')
    else:
        error_message = f"Log file not found at {datetime.now()}"
        app.logger.error(error_message)
        return error_message, 404

if __name__ == '__main__':
    app.run(debug=True)