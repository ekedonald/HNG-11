# Messaging System with RabbitMQ/Celery and Python Application behind Nginx

## Objective
Deploying a Python application behind Nginx that interacts with RabbitMQ/Celery for email sending and logging functionality.

### Prerequisites
- Vagrant (Ubuntu 22.04 Box Image)

## Implementation
The following steps are taking to deploy a Python application behind Nginx that interacts RabbitMQ/Celery for email sending functionality.

### Step 1: Install RabbitMQ, Python, Pip and Dependencies

- Run the following commands to install the applications and dependencies:

```sh
sudo apt update
sudo apt install rabbitmq-server -y
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo apt install python3-pip python3.10-venv celery -y
```

### Step 2: Create the Log file and Directory where all Python Scripts will be stored

- Run the following command to create the log file and assign file permissions and ownership:

```sh
sudo touch /var/log/messaging_system.log
sudo chmod 666 /var/log/messaging_system.log
sudo chown www-data:www-data /var/log/messaging_system.log
sudo usermod -a -G www-data $USER
```

- Create and enter the `messaging_system` where the python scripts will be stored in:

```sh
mkdir messaging_system && cd messaging_system
```

### Step 3: Create and Configure Python Scripts 

- Create the `app.py` that has the functionality of implementing a messaging system with email sending capabilities and logging. This is a breakdown of its components:

    1. **Imports**: The file imports modules for `Flask`, `Celery`, email handling, logging and environment variable management.

    2. **Flask App Configuration**: It creates a Flask App and configures `Celery` for serial task processing.

    3. **Logging**: The application sets up a rotating file handler for logging which writes logs to `/var/log/messaging_system.log`

    4. **Email Sending Task**: This is a **Celery** task `send_email` that handles sending emails using **Gmail SMTP Server**. It also populates the `/var/log/messaging_system.log` when an email is sent is sent successfully or not.

    5. **Main Route** `/`: It handles `sendmail` requests by queueing an email sending task and `talktome` requests by logging the request time. It also provides a **welcome message** if no parameters are passed.

    6. **Logs Route** `/logs`: Permits viewing of the log file on a URL.

    7. The application runs in debug mode when executed directly.

```sh
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
```
_app.py_

- The `celery_worker.py` file is used to run **Celery** separately from the main **Flask** application which allows for scalability and resource management. When executed, it processes tasks from the queue defined in the main application. This is a breakdown of its components:

    1. `from app import celery, app`: Imports the **Celery** instance and Flask app from `app.py`.

    2. `if __name__ == '__main__'`: Ensures that the code only runs when the script is executed directly not when it's imported as a module.

    3. `app.app_context()`: Ensures that any Flask-specific operations or configurations are available to the **Celery** tasks.

    4. `celery.start()`: Starts the **Celery** worker process.

```sh
from app import celery, app

if __name__ == '__main__':
    with app.app_context():
        celery.start()
```
_celery_worker.py_

- Create the `requirements.txt` file where all the packages and libraries needed for the projects to function.

```sh
cat << EOF | tee requirements.txt
flask
celery
gunicorn
python-dotenv
EOF
```

- Create a `.env` file where sensitive information will be stored.

```sh
cat <<EOF | tee .env
EMAIL_PASSWORD=<gmail_app_password>
EOF
```

- Create this file `__init__.py`.

```sh
touch __init__.py
```

### Step 4: Setup, Activate Python Virtual Environment and Install the Necessary Python Packages for the Messaging System

Python Virtual Environment is allows you have project-specific dependencies without interfering with other projects. It is best practice in Python Development.

- The commands shown below creates a new virtual environment called `venv` in the current directory and activates the virtual environment respectively.

```sh
python3 -m venv venv
source venv/bin/activate
```

- Run the commands below to install the necessary Python packages for the messaging system.

```sh
pip install flask celery[rabbitmq] python-dotenv gunicorn
```

### Step 5: Start the Celery Worker Process and Flask App

- Run the following the command to start the Celery Worker Process

```sh
nohup celery -A celery_worker.celery worker --loglevel=info > /dev/null 2>&1 &
```

- Run this command to start the `Gunicorn HTTP Server` to run the Flask Application:

```sh
nohup gunicorn -w 4 -b 127.0.0.1:8000 app:app > /dev/null 2>&1 &
```
_**Note**: `-w 4` specifies 4 worker processes to handle requests and `-b 127.0.0.1:8000` binds the server to **localhost** on port **8000**._

### Step 6: Install and Configure Nginx

- Run the command shown below to install nginx.

```sh
sudo apt install nginx -y
```

- Create and configure an nginx configuration file that gives nginx the functionality of a `Reverse Proxy` for the `Gunicorn` server and provides access to the  `/logs` path.

```sh
server {
    listen 80;
    server_name 127.0.0.1 localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /logs {
        alias /var/log/messaging_system.log;
        default_type text/plain;
        add_header Content-Type text/plain;
    }
}
```
_/etc/nginx/sites-available/messaging_system_

- Create a soft link to the `/etc/nginx/sites-enabled/` directory.

```sh
sudo ln -s /etc/nginx/sites-available/messaging_system /etc/nginx/sites-enabled/
```
- Remove the default nginx configuration files to avoid conflicts.

```sh
sudo rm /etc/nginx/sites-available/default && sudo rm /etc/nginx/sites-enabled/default
```

- Validate the new configuration file.

```sh
sudo nginx -t
```

- Restart the nginx server.

```sh
sudo systemctl restart nginx
```

### Step 7: Testing & Verification

- Run the following the commands to test the endpoints

```sh
curl localhost:80?talktome
curl localhost:8000?sendmail=<EMAIL>
curl localhost:80?sendmail=ejekkekekeke
```

- Go to the `Celery Window` terminal to view logs, a mail will also be sent the `email-address` you specified.

### Step 8: Ngrok Installation and Setup

- Sign up on [ngrok](https://ngrok.com).

- Choose your preferred agent (i.e. Linux)

- Install `ngrok`.

```sh
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
	| sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
	&& echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
	| sudo tee /etc/apt/sources.list.d/ngrok.list \
	&& sudo apt update \
	&& sudo apt install ngrok
```

- Run the following command to add your authtoken to the default ngrok.yml:

```sh
ngrok config add-authtoken <token>
```

- Deploy the application app online and select the `Static Domain` option and so the URL does not change.

```sh
ngrok http --domain=<generated-url> 80
```

![ngrok](./images/ngrok.png)

_**Note**: If you want to run ngrok in the background, run this command: `nohup ngrok http --domain=ngrok_domain_url 80 > /dev/null 2>&1 &`_

- Go to the your browser, paste the link highlighted above and click on `Visit site`.

```sh
https://ngrok_url
```

![visit site](./images/visit%20site.png)
![http url](./images/http_url.png)

- Then append the `?sendmail` and `?talktome` endpoints to the **ngrok URL** test if it works.

```sh
https://<ngrok_url>/?sendmail=<email_address>
https://<ngrok_url>/?talktome
```

- Check if the `/logs` can be accessed.

```sh
https://<ngrok_url>/logs
```

![https logs](./images/https%20logs.png)