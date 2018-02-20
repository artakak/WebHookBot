# -*- coding: utf-8 -*-
import flask
import telebot
import logging


API_TOKEN = '548697540:AAHbO142Q-p98C0-uvqpvi2-eYnSd4RdWno'

WEBHOOK_HOST = 'fc823ddf.ngrok.io'
WEBHOOK_PORT = 80  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = 'C:\Users\win7_test\PycharmProjects\WebHookBot\YOURPUBLIC.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = 'C:\Users\win7_test\PycharmProjects\WebHookBot\YOURPRIVATE.key'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
#openssl req -newkey rsa:2048 -sha256 -nodes -keyout YOURPRIVATE.key -x509 -days 365 -out YOURPUBLIC.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=fc823ddf.ngrok.io"
#
#curl -F "url=https://fc823ddf.ngrok.io/548697540:AAHbO142Q-p98C0-uvqpvi2-eYnSd4RdWno/" -F "certificate=YOURPUBLIC.pem" "https://api.telegram.org/bot548697540:AAHbO142Q-p98C0-uvqpvi2-eYnSd4RdWno/setwebhook"
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
    print bot.get_webhook_info()
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


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


# Remove webhook, it fails sometimes the set if there is a previous webhook
#bot.remove_webhook()

# Set webhook
#bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        #ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)

if __name__ == "__main__":
    app.run()