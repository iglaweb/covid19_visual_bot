# -*- coding: utf-8 -*-
"""Main module"""
import logging
import os

import telegram
from bottle import Bottle, response, request as bottle_request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

import io_utils
import plot_utils
import tg_utils
import virus_utils
from models import Countries, Country, GraphType, StatType

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBot:

    def error(update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def __init__(self, token: str):
        self.tgBOT = telegram.Bot(token=token)

    def run(self, bottle: Bottle):
        bottle.route('/api', callback=self.post_handler, method="POST")

    def send_message(self, text, chat_id: int, reply_to_message_id=None):
        """
        Prepared data should be json which includes at least `chat_id` and `text`
        """
        self.tgBOT.sendMessage(chat_id=chat_id, text=text, reply_to_message_id=reply_to_message_id)

    def prompt_select_new_country(self, chat_id: int):
        temp_list = []
        keyboard = []

        items = Countries.__members__.items()
        length = len(items)
        if length % 4 == 0:
            rows_per_item = 4
        else:
            rows_per_item = 3
        idx = 0
        for name, member in items:
            str_val = member.displayString
            int_val = member.displayValue

            if idx > 0 and idx % rows_per_item == 0:  # 4 4 3 3
                keyboard.append(temp_list)  # construct lines
                temp_list = []
            temp_list.append(InlineKeyboardButton(str_val, callback_data=int_val))
            idx = idx + 1
        keyboard.append(temp_list)

        reply_markup = InlineKeyboardMarkup(keyboard)
        self.tgBOT.sendMessage(chat_id=chat_id,
                               text="Select your country",
                               reply_markup=reply_markup)

    def react_stats_option(self, text: str, chat_id: int, user_id: int) -> bool:
        # for debugging purposes only
        if io_utils.is_local_run():
            print("got text message :", text)
        # the first time you chat with the bot AKA the welcoming message
        if text == "/start" or text == "/help":
            bot_welcome = """
                     Welcome to COVID-19 Visual bot. I visualize statistics related to COVID-19.

                     Send command /stats to get statistics for whole world or country.
                     Send command /country to select your country
                     """
            self.tgBOT.sendMessage(chat_id=chat_id, text=bot_welcome)
            return True

        if text == '/country':
            self.prompt_select_new_country(chat_id)
            return True

        if text == '/stats':
            country = virus_utils.read_pref_country(user_id=user_id)
            self.buildMenuSendMessage(chat_id, country)
            return True

        if text == '/test':
            self.tgBOT.sendMessage(chat_id=chat_id,
                                   text="There was a problem in the name you used, please enter different name")
            return True

        if text == '/cases_week' or text == '‎🌏 Cases AVG':
            self.send_photo_tg_general(stat_type=StatType.CONFIRMED, chat_id=chat_id,
                                       graph_type=GraphType.CONFIRMED_WEEK)
            return True

        if text == '/fatal_week' or text == '‎🌏 Fatal AVG':
            self.send_photo_tg_general(stat_type=StatType.DEATHS, chat_id=chat_id,
                                       graph_type=GraphType.DEATHS_WEEK)
            return True

        if text == '/cases_per_1m' or text == '‎🌏 Cases per 1M':
            self.send_photo_tg_general(stat_type=StatType.CONFIRMED, chat_id=chat_id,
                                       graph_type=GraphType.CONFIRMED_1M_PEOPLE)
            return True

        if text == '/cases_bar' or text == '‎🌏 Cases (bar)':
            self.send_photo_tg_general(stat_type=StatType.CONFIRMED, chat_id=chat_id,
                                       graph_type=GraphType.CONFIRMED_BAR)
            return True

        if text == '/fatal_bar' or text == '‎🌏 Fatal (bar)':
            self.send_photo_tg_general(stat_type=StatType.DEATHS, chat_id=chat_id,
                                       graph_type=GraphType.DEATHS_BAR)
            return True

        if text == '/cases' or text == '‎🌏 Cases':
            self.send_photo_tg_general(stat_type=StatType.CONFIRMED, chat_id=chat_id,
                                       graph_type=GraphType.CONFIRMED_TOTAL)
            return True

        if text == '/fatal' or text == '‎🌏 Fatal':
            self.send_photo_tg_general(stat_type=StatType.DEATHS, chat_id=chat_id,
                                       graph_type=GraphType.DEATHS_TOTAL)
            return True

        for name, member in Countries.__members__.items():
            int_val = member.displayValue
            flag = member.displayFlag
            country_value = member.value

            if text == f'/{int_val}_fatal_total' or text == f"{flag} Total Fatal":
                self.send_photo_tg_country_total(stat_type=plot_utils.StatType.DEATHS, chat_id=chat_id,
                                                 graph_type=GraphType.DEATHS_TOTAL,
                                                 country_name=country_value)
                return True

            if text == f'/{int_val}_cases_total' or text == f"{flag} Total Cases":
                self.send_photo_tg_country_total(stat_type=StatType.CONFIRMED, chat_id=chat_id,
                                                 graph_type=GraphType.CONFIRMED_TOTAL,
                                                 country_name=country_value)
                return True

            if text == f'/{int_val}_fatal_daily' or text == f"{flag} Daily Fatal":
                self.send_photo_tg_country_active(stat_type=StatType.DEATHS, chat_id=chat_id,
                                                  graph_type=GraphType.DEATHS_ACTIVE,
                                                  country_name=country_value)
                return True

            if text == f'/{int_val}_cases_daily' or text == f"{flag} Daily Cases":
                self.send_photo_tg_country_active(stat_type=StatType.CONFIRMED, chat_id=chat_id,
                                                  graph_type=GraphType.CONFIRMED_ACTIVE,
                                                  country_name=country_value)
                return True

    def post_handler(self):
        data = bottle_request.json
        update = telegram.Update.de_json(data, self.tgBOT)
        query = update.callback_query

        is_bot = update.effective_user.is_bot
        if is_bot:
            print('Bot detected')
            return

        user_id = update.effective_user.id
        if io_utils.is_local_run():
            print(f'USER ID: {user_id}, name: {update.effective_user.username}')

        if query is not None:
            option = query.data

            if option in Countries.__members__:  # check if country value in members
                country = Countries[option]
                virus_utils.write_pref_country(user_id, country)
                query.edit_message_text(text="Selected option: {}".format(country.displayString))

                chat_id = query.message.chat_id
                self.buildMenuSendMessage(chat_id, country)
            else:
                print(f'Country {option} not found in list!')
            return

        if update.message is None:
            print('Message is empty')
            return

        chat_id = update.message.chat_id
        msg_id = update.message.message_id

        # Telegram understands UTF-8, so encode text for unicode compatibility
        text_pure = update.message.text
        if text_pure is None:
            print('Text is empty')
            return

        text = text_pure.encode('utf-8').decode()
        reacted = self.react_stats_option(text=text, chat_id=chat_id, user_id=user_id)
        if reacted:
            return

        self.send_message(text='No option selected', chat_id=chat_id)
        return response

    def buildMenuSendMessage(self, chat_id: int, country: Country):
        self.tgBOT.sendMessage(chat_id, 'Select keyboard option',
                               reply_markup=ReplyKeyboardMarkup(
                                   resize_keyboard=True,
                                   keyboard=[
                                       [
                                           KeyboardButton(text="‎🌏 Cases AVG"),
                                           KeyboardButton(text="‎🌏 Fatal AVG"),
                                           KeyboardButton(text="‎🌏 Cases per 1M")
                                       ],
                                       [
                                           KeyboardButton(text="‎🌏 Cases"),
                                           KeyboardButton(text="‎🌏 Fatal"),
                                           KeyboardButton(text="‎🌏 Cases (bar)"),
                                           KeyboardButton(text="‎🌏 Fatal (bar)")
                                       ],
                                       [
                                           KeyboardButton(text=f"{country.displayFlag} Total Cases"),
                                           KeyboardButton(text=f"{country.displayFlag} Total Fatal"),
                                           KeyboardButton(text=f"{country.displayFlag} Daily Cases"),
                                           KeyboardButton(text=f"{country.displayFlag} Daily Fatal")
                                       ]
                                   ],
                                   one_time_keyboard=False
                               ))

    def send_photo_tg_country(self, active: bool, stat_type: StatType, country: Country, chat_id: int,
                              graph_type: GraphType):
        photo_url = io_utils.get_photo_path_country(graph_type, country_name=country.value)
        need_data = virus_utils.should_update_data()

        if need_data is False and os.path.exists(photo_url):
            photo_stream = open(photo_url, 'rb')
            tg_utils.send_photo_file(self.tgBOT, photo_stream, chat_id)
        else:
            if active:
                plot_tuple = plot_utils.generate_country_active_plot(country, stat_type)
            else:
                plot_tuple = plot_utils.generate_country_total_plot(country, stat_type)

            if plot_tuple is not None:
                fig, ax = plot_tuple
                tg_utils.send_photo_fig(self.tgBOT, chat_id=chat_id, fig=fig, graph_type=graph_type,
                                        country=country)

    def send_photo_tg_country_active(self, stat_type: StatType, country_name: Country, chat_id: int,
                                     graph_type: GraphType):
        self.send_photo_tg_country(True, stat_type, country_name, chat_id, graph_type)

    def send_photo_tg_country_total(self, stat_type: StatType, country_name: Country, chat_id: int,
                                    graph_type: GraphType):
        self.send_photo_tg_country(False, stat_type, country_name, chat_id, graph_type)

    def send_photo_tg_general(self, stat_type: StatType, chat_id: int, graph_type: GraphType):
        photo_url = io_utils.get_photo_path_world(graph_type)
        need_data = virus_utils.should_update_data()

        if need_data is False and os.path.exists(photo_url):  # no data need and photo exists -> return
            photo_stream = open(photo_url, 'rb')
            tg_utils.send_photo_file(self.tgBOT, photo_stream, chat_id)
        else:  # get new data or rewrite existing one

            if graph_type == GraphType.CONFIRMED_1M_PEOPLE:
                plot_tuple = plot_utils.generate_world_stat_10_per_million(stat_type)
            elif graph_type == GraphType.CONFIRMED_BAR or \
                    graph_type == GraphType.DEATHS_BAR or \
                    graph_type == GraphType.RECOVERED_BAR:
                plot_tuple = plot_utils.generate_bar_world_stat_10(stat_type)
            elif graph_type == GraphType.CONFIRMED_WEEK or \
                    graph_type == GraphType.DEATHS_WEEK or \
                    graph_type == GraphType.RECOVERED_WEEK:
                plot_tuple = plot_utils.generate_toll_plot_avg(stat_type)
            else:
                plot_tuple = plot_utils.generate_world_stat_10(stat_type)

            if plot_tuple is not None:
                fig, ax = plot_tuple
                tg_utils.send_photo_fig(self.tgBOT, chat_id=chat_id, fig=fig, graph_type=graph_type)
            else:
                print('Plot not constructed ' + graph_type.to_name())
