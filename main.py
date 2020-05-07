# -*- coding: utf-8 -*-
"""Main module"""
import os

import requests
from bottle import Bottle

import io_utils
from tg_bot_handler import TelegramBot

app = Bottle(False)


@app.get('/test')
def api():
    return "Completed."


@app.get("/")
def index():
    cwd = os.getcwd()
    return cwd


def run_main():
    prefs = io_utils.create_prefs_dictionary('.prefs')
    if prefs is None:
        print('Cannot continue. Preferences empty')
        return

    token_prod = prefs['token_prod']
    token_debug = prefs['token_debug']
    domain_debug = prefs['domain_debug']
    token = token_debug \
        if io_utils.is_local_run() \
        else token_prod

    telegram_base_url = f'https://api.telegram.org/bot{token}/'  # <--- add your telegram token here; it should be like https://api.telegram.org/bot12345678:SOMErAn2dom/
    tg_bot = TelegramBot(token=token)
    tg_bot.run(app)

    if io_utils.is_local_run():
        print('Running')
        domain = domain_debug
        url = f'{telegram_base_url}setWebHook?url={domain}/api'
        req = requests.get(url)
        if req.status_code == requests.codes.ok:
            print('Set web hook!')
            print(req.text)

        app.run(host='localhost', port=8090)


if __name__ == '__main__':
    run_main()
