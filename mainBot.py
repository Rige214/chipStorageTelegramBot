import configuration
import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot(configuration.tokenTestBot)
userChips = None

@bot.message_handler(commands=['start'])
def message_start(message):
    userName = message.from_user.first_name
    userId = message.from_user.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info = types.KeyboardButton(text='/info')
    setChips = types.KeyboardButton(text='/setChips')
    statistics = types.KeyboardButton(text='/stats')
    top = types.KeyboardButton(text='/top')
    markup.add(info, setChips, statistics, top)
    bot.send_message(message.chat.id, f'Приветствую,<strong> {userName} !</strong>\n'
        f'Бот создан для хранения информации о фишках. Пожалуйста, пользуйтесь исключительно кнопками',
        parse_mode="HTML", reply_markup=markup)

    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users (telegramId,username,chips) VALUES (?, ?, ?)', (userId, userName, 0))
    connection.commit()
    connection.close()

@bot.message_handler(commands=['setChips'])
def set_chips(message):
    bot.send_message(message.chat.id, f'Введите количество фишек', parse_mode="HTML")
    bot.register_next_step_handler(message, us_chips)
def us_chips(message):
    global userChips
    userChips = message.text.strip()
    usId = message.from_user.id
    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE Users SET chips = ? WHERE telegramId = ?", (userChips, usId))
    print(usId, userChips)
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, f'Текущее количество фишек - <code>{userChips}</code> !', parse_mode="HTML")


@bot.message_handler(commands=['info'])
def get_info(message):
    usId = message.from_user.id

    connection = sqlite3.connect('pRes.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE telegramId = ?", (usId,))
    res = cursor.fetchall()
    if(usId == res[0][0]):
        userId = res[0][0]
        userName = res[0][1]
        userChips = res[0][2]
    else:
        print('error penis')
    connection.commit()
    connection.close()

    bot.send_message(message.chat.id,
        f'Приветствую, <strong>{userName} !</strong>\n'
        f'Количество твоих фишек = <code>{userChips}</code> .', parse_mode="HTML")


@bot.message_handler(commands=['stats'])
def use_text(message):
    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name}, раздел <code>{message.text}</code> в разработке!'
                     , parse_mode="HTML")


@bot.message_handler(commands=['top'])
def get_info(message):
    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name}, раздел <code>{message.text}</code> в разработке!'
                     , parse_mode="HTML")


@bot.message_handler(content_types=['text'])
def use_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, пожалуйста, воспользутесь кнопками')


bot.infinity_polling()