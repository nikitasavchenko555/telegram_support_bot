# -*- coding: utf-8 -*-
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

import config
import sqlite3
import telebot
import requests
import re

Support_Bot = telebot.TeleBot(config.token)


@Support_Bot.message_handler(regexp="[^start][^joke][^story][^help][^location]")
def check_enter(message):
    text = """Введите что-нибудь другое:)
    Основные команды бота:
    /start = поздороваться с ботом:)
    /joke = получить шутку
    /story = получить историю
    /help = получить справку"""
    Support_Bot.send_message(message.chat.id, text)


@Support_Bot.message_handler(commands=['start'])
def start(message):
    print('start')
    try:
        conn_base = sqlite3.connect("telegram_base.db")
    except sqlite3.OperationalError:
        print("Извините, База Данных временно недоступна")
    cursor = conn_base.cursor()
    try:
        cursor.execute(
            """select id_user, user_name from users_list where id_user = {id_u}""".format(id_u=message.chat.id))
    except sqlite3.OperationalError:
        cursor.execute('CREATE TABLE IF NOT EXISTS users_list(id_user integer, user_name text)')
    list_user = str(cursor.fetchall())
    user_id = re.findall(r'[0-9]{8,10}', list_user)
    user_id = re.sub("(\['|\'])", '', str(user_id))
    user_name = re.findall(r'[А-Яа-я]{3,15}', list_user)
    user_name = re.sub("(\['|\'])", '', str(user_name))
    if user_id == str(message.chat.id):
        Support_Bot.send_message(message.chat.id, 'Привет, {name}!'.format(name=user_name))
    else:
        sent = Support_Bot.send_message(message.chat.id, 'Как тебя зовут?')
        Support_Bot.register_next_step_handler(sent, hello)


def hello(message):
    user_name = message.text
    user_id = str(message.chat.id)
    Support_Bot.send_message(message.chat.id,
                             'Привет, {name_user}. Рад Вас видеть.'.format(name_user=user_name))
    conn_base = sqlite3.connect("telegram_base.db")
    cursor = conn_base.cursor()
    cursor.execute("""insert into users_list
    values (:id, :name)""", {"id": user_id, "name": user_name})
    conn_base.commit()


@Support_Bot.message_handler(commands=['help'])
def get_help(message):
    text = """Основные команды бота:
    /start = поздороваться с ботом:)
    /joke = получить шутку
    /story = получить историю
    /help = получить справку"""
    Support_Bot.send_message(message.chat.id, text)


@Support_Bot.message_handler(commands=['joke'])
def get_joke(message):
    # парсим регуляркой, т.к. response.json() не работает
    response = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=1')
    text = response.text
    text = re.sub('{"content":"', '', text)
    text = re.sub('\"}', '', text)
    Support_Bot.send_message(message.chat.id, text)


@Support_Bot.message_handler(commands=['story'])
def get_story(message):
    # парсим регуляркой, т.к. response.json() не работает
    response = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=2')
    text = response.text
    text = re.sub('{"content":"', '', text)
    text = re.sub('\"}', '', text)
    Support_Bot.send_message(message.chat.id, text)


@Support_Bot.message_handler(commands=['location'])
def get_location(message):
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    Support_Bot.send_message(message.chat.id, "Пожалуйста, нажмите на кнопку, чтобы передать местоположение. \n"
                                              "Не забудьте включить геолокацию:)",
                             reply_markup=keyboard)


@Support_Bot.message_handler(content_types=['location'])
def save_location(message):
    if message.location is not None:
        print(message.location.latitude, message.location.longitude)

if __name__ == '__main__':
    Support_Bot.polling(none_stop=True)
