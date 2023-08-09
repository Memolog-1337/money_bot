import telebot

import pytz

from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from datetime import datetime, timedelta

import base.postgre as bd

BOT_TOKEN = '6185918971:AAHXzhysHACbkxhV8ZqwtImvPBcNat-5s1s'
TIMEZONE = pytz.timezone('Europe/Moscow')
DATETIME_MASK = '%d.%m.%Y'

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    bd.add_user_to_bd(message.chat.id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    check = KeyboardButton('/check')
    statistics = KeyboardButton('/statistics')
    categories = KeyboardButton('/categories')
    balance = KeyboardButton('/balance')
    markup.add(check)
    markup.add(statistics)
    markup.add(categories)
    markup.add(balance)
    bot.send_message(
        message.chat.id,
        'Hi',
        reply_markup=markup
    )


@bot.message_handler(commands=['check'])
def check_finances(message):
    markup = InlineKeyboardMarkup()
    delete = InlineKeyboardButton('Удалить запись', callback_data='delete')
    change = InlineKeyboardButton('Изменить запись', callback_data='change')
    markup.add(change, delete)
    responce = bd.get_all_data_in_finances(message.chat.id)
    bot.send_message(
        message.chat.id,
        responce,
        reply_markup=markup
    )


@bot.message_handler(commands=['statistics'])
def get_statistics(message):
    markup = InlineKeyboardMarkup()
    today = InlineKeyboardButton('Сегодня', callback_data='statistics:today')
    yesterday = InlineKeyboardButton('Вчера', callback_data='statistics:yesterday')
    last_week = InlineKeyboardButton('Последняя неделя', callback_data='statistics:last_week')
    interval = InlineKeyboardButton('Промежуток времени', callback_data='statistics:interval')
    markup.add(today, yesterday)
    markup.add(last_week)
    markup.add(interval)

    bot.send_message(
        message.chat.id,
        'Выберите промежуток времени',
        reply_markup=markup
    )


@bot.message_handler(commands=['categories'])
def get_categories(message):
    responce = bd.get_categories()

    bot.send_message(
        message.chat.id,
        responce
    )


@bot.message_handler(commands=['balance'])
def get_balance(message):
    balance = bd.get_user_balance(message.chat.id)

    bot.send_message(
        message.chat.id,
        f'Ваш баланс на данный момент: {balance} рублей'
    )


@bot.message_handler(content_types=['text'])
def add_row(message):
    date = datetime.now(tz=TIMEZONE).date()
    text = message.text.strip()
    amount, category, *comment = text.split()
    balance = bd.add_row_to_finances(date, float(amount), message.chat.id, category, ' '.join(comment))
    bot.send_message(
        message.chat.id,
        f'Запись добавлена \n'
        f'Ваш баланс на данный момент: {balance} рублей'
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'delete':
        bot.send_message(
            call.message.chat.id,
            'Пришлите номер записи, которую хотите удалить'
        )
        bot.register_next_step_handler(call.message, delete_row)
    elif call.data == 'change':
        bot.send_message(
            call.message.chat.id,
            'Пришлите номер записи, которую хотите изменить'
        )
        bot.register_next_step_handler(call.message, get_parametr)
    elif 'change:' in call.data:
        name_parametr, key = call.data.split(':')[1:]
        bot.send_message(
            call.message.chat.id,
            'Пришлите новое значение параметра'
        )
        bot.register_next_step_handler(call.message, update_row_finances, name_parametr, key)

    elif call.data == 'statistics:interval':
        bot.send_message(
            call.message.chat.id,
            'Пришлите интервал поиска'
        )
        bot.register_next_step_handler(call.message, get_statistics_for_interval, 'interval')

    elif 'statistics:' in call.data:
        name_interval = call.data.split(':')[1:][0]
        get_statistics_for_interval(call.message, name_interval)


def delete_row(message):
    key = int(message.text.strip())
    bd.delete_row_from_finaces(key)
    bot.send_message(
        message.chat.id,
        f'Запись {key} удалена'
    )


def get_parametr(message):
    key = int(message.text.strip())
    markup = InlineKeyboardMarkup()
    date = InlineKeyboardButton('Дата', callback_data=f'change:time:{key}')
    amount = InlineKeyboardButton('Стоимость', callback_data=f'change:amount:{key}')
    category = InlineKeyboardButton('Категория', callback_data=f'change:category_id:{key}')
    comment = InlineKeyboardButton('Комментарий', callback_data=f'change:comment:{key}')
    markup.add(date, amount)
    markup.add(category, comment)
    bot.send_message(
        message.chat.id,
        'Выберите категорию',
        reply_markup=markup
    )


def update_row_finances(message, name_parametr, key):
    new_value = message.text.strip()

    if name_parametr == 'amount':
        new_value = float(new_value)
        old_value = bd.get_row_from_table('users', 'chat_id', message.chat.id)
        old_value = old_value[2]
        bd.update_user_balance(message.chat.id, new_value - old_value)

    elif name_parametr == 'category_id':
        new_value = bd.get_category_id(new_value.lower())

    elif name_parametr == 'time':
        new_value = datetime.strptime(new_value, '%d.%m.%Y').date()

    bd.update_row_in_table('finances', key, name_parametr, new_value)
    bot.send_message(
        message.chat.id,
        'Изменено'
    )


def get_statistics_for_interval(message, name_interval):
    responce = 'Не найдено'
    markup = InlineKeyboardMarkup()
    delete = InlineKeyboardButton('Удалить запись', callback_data='delete')
    change = InlineKeyboardButton('Изменить запись', callback_data='change')
    markup.add(change, delete)

    if name_interval == 'today':
        day = datetime.now(tz=TIMEZONE).date()
        responce = bd.get_data_in_finances_from_day(message.chat.id, day)

    elif name_interval == 'yesterday':
        today = datetime.now(tz=TIMEZONE).date()
        day = today - timedelta(days=1)
        responce = bd.get_data_in_finances_from_day(message.chat.id, day)

    elif name_interval == 'last_week':
        end_date = datetime.now(tz=TIMEZONE).date()
        start_date = end_date - timedelta(days=end_date.weekday())
        responce = bd.get_data_in_finances_from_interval(message.chat.id, start_date, end_date)

    elif name_interval == 'interval':
        dates = message.text.strip()
        start_date, end_date = dates.split('-')
        start_date = datetime.strptime(start_date, '%d.%m.%Y').date()
        end_date = datetime.strptime(end_date, '%d.%m.%Y').date()
        responce = bd.get_data_in_finances_from_interval(message.chat.id, start_date, end_date)

    bot.send_message(
        message.chat.id,
        responce,
        reply_markup=markup
    )


def main():
    bd.init_db()
    category_names = [
        'Еда',
        'Квартплаты',
        'Развлечения',
        'Свидания',
        'Одежда',
        'Мафия',
        'Подарки',
        'Такси',
        'Кальян/Сигареты',
        'Долги',
        'Зарплата',
        'Премия',
        'Подработка',
        'Покер',
    ]

    for name in category_names:
        bd.add_category_to_bd(name)

    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
