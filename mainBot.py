import configuration
import telebot
from telebot import types
import sqlite3
from heapq import nlargest
from operator import itemgetter


bot = telebot.TeleBot(configuration.tokenTestBot)
USER_CHIPS = None

@bot.message_handler(commands=['start'])
def message_start(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info = types.KeyboardButton(text='/info')
    set_chip = types.KeyboardButton(text='/setChips')
    statistics = types.KeyboardButton(text='/stats')
    top = types.KeyboardButton(text='/top')
    markup.add(info, set_chip, statistics, top)
    bot.send_message(message.chat.id, f'Приветствую,<strong> {user_name} !</strong>\n'
        f'Бот создан для хранения информации о фишках. Пожалуйста, пользуйтесь исключительно кнопками',
        parse_mode="HTML", reply_markup=markup)

    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE telegramId = ?", (user_id,))
    result = cursor.fetchall()
    if (user_id == result[0][1]):
        print("Уже существует такой игрок", user_id, " - ", user_name)
        bot.send_message(message.chat.id, f'Вы уже зарегистрированы', parse_mode="HTML")
    else:
        connection = sqlite3.connect('pRes.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Users (telegramId,username,chips) VALUES (?, ?, ?)', (user_id, user_name, None))
        connection.commit()
        connection.close()


@bot.message_handler(commands=['setChips'])
def set_chips(message):
    bot.send_message(message.chat.id, f'Введите количество фишек', parse_mode="HTML")
    bot.register_next_step_handler(message, us_chips)


def us_chips(message):
    global USER_CHIPS
    USER_CHIPS = message.text.strip()
    user_id = message.from_user.id
    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE Users SET chips = ? WHERE telegramId = ?", (USER_CHIPS, user_id))
    print(user_id, USER_CHIPS)
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, f'Текущее количество фишек - <code>{USER_CHIPS}</code> !', parse_mode="HTML")


@bot.message_handler(commands=['info'])
def get_info(message):
    user_id = message.from_user.id

    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE telegramId = ?", (user_id,))
    result = cursor.fetchall()
    if(user_id == result[0][1]):
        user_name = result[0][2]
        user_chips = result[0][3]
    else:
        print('error penis get_info')
    connection.commit()
    connection.close()

    bot.send_message(message.chat.id,
        f'Приветствую, <strong>{user_name} !</strong>\n'
        f'Количество твоих фишек = <code>{user_chips}</code> .', parse_mode="HTML")


@bot.message_handler(commands=['stats'])
def get_stats(message):
    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name}, раздел <code>{message.text}</code> в разработке!'
                     , parse_mode="HTML")


@bot.message_handler(commands=['top'])
def get_top(message):
    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute("SELECT userName, chips FROM Users")
    result = cursor.fetchall()
    for name, chips in nlargest(3, result, key=itemgetter(1)):
        print(name, chips)
        bot.send_message(message.chat.id,
                 f'Имя - {name}, фишки - <code>{chips}</code>', parse_mode="HTML")


@bot.message_handler(content_types=['text'])
def use_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, пожалуйста, воспользутесь кнопками')


bot.infinity_polling()