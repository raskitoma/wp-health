#############################################
# Website Health - config.py
# (c)2022, Raskitoma.com
#--------------------------------------------
# Master config file
#-------------------------------------------- 
# TODO  Check functionality
# TODO  Check if this is the right place for this
#-------------------------------------------- 

# Include libraries for functionality
from asyncio.windows_events import NULL
import os, sys
import logging
import string
import random
from flask import Flask, \
    Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from celery import Celery
from slack_sdk.webhook import WebhookClient

# Prepping logger
logging.getLogger().setLevel(logging.INFO)

APP_PORT = int(os.environ.get('PORT', 5000))
REDIS_INSTANCE  = os.environ.get('REDIS_INSTANCE', 'redis://redis:6379') + '/0'
CHECK_TIMER = int(os.environ.get('CHECK_TIMER', '300'))

SLACK_ENABLED = os.environ.get('SLACK_ENABLED', 'False')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK', '')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#general')

CHECK_MODE = 'ON'

if CHECK_TIMER < 300:
    sys.exit('CHECK_TIMER must be at least 300 seconds')

app = Flask(__name__)

app.config['MAIL_ENABLED'] = os.environ.get('MAIL_ENABLED', 'False')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp-relay.googlemail.com')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT', 587)
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', True)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'from@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'password')
app.config['MAIL_DEFAULT_SENDER'] = 'from@example.com'
MAIL_ENABLED = app.config['MAIL_ENABLED']
MAIL_TO = os.environ.get('MAIL_TO', 'mailto@example.com')
mail = Mail(app)

app.config['CELERY_BROKER_URL'] = REDIS_INSTANCE
app.config['CELERY_RESULT_BACKEND'] = REDIS_INSTANCE

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/website-checker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Sites(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.Text, nullable=False)
    path = db.Column(db.Text, nullable=False)
    user = db.Column(db.Text, nullable=False)
    wp_api = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return  f'"id":"{self.id}", "host":"{self.host}", "path":"{self.path}", "user":"{self.user}", "wp_api":"{self.wp_api}"'

class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    object_type = db.Column(db.Text, nullable=False)
    object_name = db.Column(db.Text, nullable=False)
    object_version = db.Column(db.Text, nullable=True)
    source_version = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f'id={self.id}, host={self.host}, date={self.date}, status={self.status}'
       
class Wpdata(db.Model):
    __tablename__ = 'wp_data'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    plugins_out = db.Column(db.Integer, nullable=False)
    themes_out = db.Column(db.Integer, nullable=False)
    version = db.Column(db.Text, nullable=False)
    # When doing a query, display each row represented 
    # by an object containing what's in the return statement
    def __repr__(self):
        return f'id={self.id}, host={self.host}, date={self.date}, status={self.status}, plugins_out={self.plugins_out}, themes_out={self.themes_out}, version={self.version}'

db.create_all()

@celery.task
def send_async_email(email_data):
    """Background task to send an email with Flask-Mail."""
    msg = Message(email_data['subject'],
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)

def send_slack(msg, channel=SLACK_CHANNEL, webhook=SLACK_WEBHOOK, enabled=SLACK_ENABLED):
    """
    Send a msg to slack
    :param msg: Message
    :param channel: Channel
    :param webhook: Webhook
    :param enabled: if Slack integration is enabled
    :return:
    """
    if enabled == 'True':
        client = WebhookClient(webhook)
        client.send_message(channel, msg)
    return Response(status=200)

def mail_send(msg, subject='[WP Website Health] - Alert!', sender=app.config['MAIL_DEFAULT_SENDER'], mail_to=MAIL_TO, enabled=MAIL_ENABLED):
    email_data = {
        'subject': subject,
        'to': mail_to,
        'body': msg
    }

    if enabled == 'True':
        send_async_email.delay(email_data)
        print('Sending email to {0}'.format(mail_to))

    return Response(status=200)

def check_process():
    import subprocess
    script_name = "engine.py"
    cmd='pgrep -f .*python.*{}'.format(script_name)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    my_pid, err = process.communicate()
    if len(my_pid.splitlines()) >0:
        print("Script Running in background")
        return True
    else:
        print("Script not running in background")
        return False

def load_dummy_sites():
    # Load dummy sites   
    return { "data" : [
        {
            'id' : '0',
            'host' : 'https://site.com',
            'path' : '/wp-json/wp/v2/plugins/',
            'user' : 'admin',
            'wp_api' : 'abcd efgh 0123 4567 890a bcde'
        }
    ]} 

def load_sites():
    sites = Sites.query.all()
    if sites is not None:
        result = "{ \"data\" : [ "
        for site in sites:
            # logging.info(site)
            result=result+"{"+str(site)+"},"
        result=result[:-1]+"]}"
    else:
        result = load_dummy_sites()
    return result

def random_key():
    """
    Generate and returns a random string
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

def add_site(host, path, file, key, wp_api):
        db.session.add(Sites(
            host = host,
            path = path,
            file = file,
            key = key,
            wp_api = wp_api
        ))
        logging.INFO('Added site: ' + host, path, file, key, wp_api)
        db.session.commit()


#############################################
# EoF    