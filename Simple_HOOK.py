# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
import flask
import telebot
import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

API_TOKEN = 'Bot_token'

WEBHOOK_HOST = 'HOSTNAME'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '127.0.0.1'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = "%s/YOURPUBLIC.pem" % dir_path  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = "%s/YOURPRIVATE.key" % dir_path # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
#openssl req -newkey rsa:2048 -sha256 -nodes -keyout YOURPRIVATE.key -x509 -days 365 -out YOURPUBLIC.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=HOSTNAME"
#
#curl -F "url=https://a3fd200f.ngrok.io/BOT_TOKEN/" -F "certificate=YOURPUBLIC.pem" "https://api.telegram.org/BOT_TOKEN/setwebhook"
#

WEBHOOK_URL_BASE = "https://%s" % (WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    # Index page
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


# Handle '/end'
@bot.message_handler(commands=['send'])
def send_letter(message):
    bot.reply_to(message, "Ваше сообщение обрабатывается")


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


# Remove webhook, it fails sometimes the set if there is a previous webhook
#bot.remove_webhook()

# Set webhook
#bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))

if __name__ == '__main__':
    app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, debug=True)