# -*- coding: utf-8 -*-
"""Main module"""
import os

import requests
from bottle import Bottle

import io_utils
from tg_bot_handler import TelegramBot

token, webhook_url = io_utils.read_system_credentials()
app = Bottle(False)
tg_bot = TelegramBot(token=token)
tg_bot.run(app)


@app.get('/test')
def api():
    return "Completed."


@app.get("/")
def index():
    cwd = os.getcwd()
    return cwd


def run_main():
    if io_utils.is_local_run():
        print('Running on local machine')

        telegram_base_url = tg_bot.tgBOT.base_url
        url = f'{telegram_base_url}/setWebHook?url={webhook_url}'
        req = requests.get(url)
        if req.status_code == requests.codes.ok:
            print('Set web hook!')
            print(req.text)
        else:
            print('Cannot set webhook')

        app.run(host='localhost', port=8090)


if __name__ == '__main__':
    run_main()
