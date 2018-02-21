# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
import flask
import telebot
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PIL import Image
import time
import os
from celery import Celery


dir_path = os.path.dirname(os.path.realpath(__file__))

API_TOKEN = '548697540:AAHbO142Q-p98C0-uvqpvi2-eYnSd4RdWno'

WEBHOOK_HOST = 'fc823ddf.ngrok.io'
WEBHOOK_PORT = 80  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = "%s/YOURPUBLIC.pem" % dir_path  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = "%s/YOURPRIVATE.key" % dir_path # Path to the ssl private key

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
app.config['CELERY_BROKER_URL'] = 'redis://10.16.4.79:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'database'
app.config['CELERY_RESULT_DBURI'] = 'sqlite:///temp.db'
app.config['CELERY_TRACK_STARTED'] = True
app.config['CELERY_SEND_EVENTS'] = True

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


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


# Handle '/start' and '/help'
@bot.message_handler(commands=['send'])
def send_letter(message):
    bot.reply_to(message, "Обрабатывается")
    test.apply_async(countdown=10)
    #on_site.delay(message)


@celery.task
def test():
    time.sleep(50)


@celery.task
def on_site(message):
    driver = webdriver.PhantomJS("%s/phantomjs.exe" % dir_path, service_args=['--ignore-ssl-errors=true'])
    driver.set_window_size(1280, 1024)
    driver.get("https://xn--90adear.xn--p1ai/request_main")
    driver.find_element_by_xpath("//label[@class='checkbox']").click()
    driver.find_element_by_xpath("//button[@class='u-form__sbt']").click()

    driver.find_element_by_xpath("//select[@name='region_code']/option[text()='77 г. Москва']").click()
    driver.find_element_by_xpath("//select[@name='subunit']/option[text()='Управление ГИБДД ГУ МВД России по г. Москве']").click()
    driver.find_element_by_id("surname_check").send_keys(u"Фамилия")
    driver.find_element_by_id("firstname_check").send_keys(u"Имя")
    driver.find_element_by_id("email_check").send_keys("mail.nomail.com")
    driver.find_element_by_id("phone_check").send_keys("+7925555555")
    driver.find_element_by_name("message").send_keys(u"Обращение")

    capcha = driver.find_element_by_xpath("//img[@class='captcha-img']")
    get_captcha(driver, capcha, "%s/captcha.jpeg" % dir_path)

    driver.find_element_by_name("captcha").send_keys("captcha")

    driver.find_element_by_xpath("//a[@class='u-form__sbt']").click()
    time.sleep(5)
    driver.get_screenshot_as_file("%s/alt.png" % dir_path)

    bot.reply_to(message, "Отправлено")


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


def get_captcha(driver, element, path):
    location = element.location
    size = element.size
    driver.save_screenshot(path)

    image = Image.open(path)

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    image = image.crop((left, top, right, bottom))
    image.save(path, 'jpeg')


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