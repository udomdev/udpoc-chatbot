import os
import sys
import logging

from datetime import datetime

from flask import Flask, request, abort
from googletrans import Translator

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)
translater = Translator()

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET')
    sys.exit(1)

if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN')
    sys.exit(1)

# gunicorn_error_logger = logging.getLogger('gunicorn.error')
# app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
# app.logger.debug('this will show in the log')

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route('/')
def hello_world():
    the_time = datetime.now().strftime("%A, %d-%b-%Y %H:%M:%S")
    return """ 
    <h1>POC Line-Bot</h1>
    <p>It is currently {time}.</p>
    <img src="http://loremflickr.com/600/400">
    """.format(time=the_time)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    app.logger.info("X-Line-Signature:" + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def translate_text(text):
    en_text = translater.translate(text, dest='en').text
    return en_text


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    app.logger.info("Event: " + event.reply_token)
    app.logger.info("Text: " + event.message.text)
    translated = translate_text(event.message.text)
    reply_text = translated

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(reply_text))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
