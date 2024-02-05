import configuration
import telebot
from telebot import types
import sqlite3
from heapq import nlargest
from operator import itemgetter


bot = telebot.TeleBot(configuration.api_token)


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

    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users WHERE telegramId = ?", (user_id,))
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    if not result:
        connection = sqlite3.connect(configuration.database)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Users (telegramId,username,chips) VALUES (?, ?, ?)', (user_id, user_name, 0))

        cursor.execute("SELECT id FROM Users WHERE telegramId = ?", (user_id,))
        result_id = cursor.fetchall()
        user_bd_id = result_id[0][0]
        cursor.execute(
            'INSERT INTO stat_chips (id_users, chips_one, chips_two, chips_three, chips_fourth) VALUES (?, ?, ?, ?, ?)',
            (user_bd_id, 0, 0, 0, 0))
        connection.commit()
        connection.close()
    else:
        bot.send_message(message.chat.id, f'Вы уже зарегистрированы', parse_mode="HTML")


@bot.message_handler(commands=['setChips'])
def set_chips(message):
    bot.send_message(message.chat.id, f'Введите количество фишек', parse_mode="HTML")
    bot.register_next_step_handler(message, us_chips)


def us_chips(message):
    user_chips = message.text.strip()
    user_id = message.from_user.id
    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()

    # Получение айди из базы
    cursor.execute("SELECT id FROM Users WHERE telegramId = ?", (user_id,))
    result_id = cursor.fetchall()
    user_bd_id = result_id[0][0]
    connection.commit()

    # 0Получение текущего кол-ва фишек для присвоения в чипс_ван
    cursor.execute("SELECT chips FROM Users WHERE id =?", (str(user_bd_id), ))
    result_chips_curr_to_one = cursor.fetchall()
    ch_curr_to_one = result_chips_curr_to_one[0][0]
    connection.commit()

    # 0Обновляем текущие фишки
    cursor.execute("UPDATE Users SET chips = ? WHERE telegramId = ?", (user_chips, user_id))
    connection.commit()

    # 1Получение чипс_ван из БД
    cursor.execute("SELECT chips_one FROM stat_chips WHERE id_users = ?", (str(user_bd_id), ))
    result_chips_one_to_two = cursor.fetchall()
    ch_one_to_two = result_chips_one_to_two[0][0]
    connection.commit()

    # 2Получение чипс_ту из БД
    cursor.execute("SELECT chips_two FROM stat_chips WHERE id_users = ?", (str(user_bd_id), ))
    result_chips_two_to_three = cursor.fetchall()
    ch_two_to_three = result_chips_two_to_three[0][0]
    connection.commit()

    # 2Обновляем чипс_ту
    connection.commit()
    cursor.execute("UPDATE stat_chips SET chips_two = ? WHERE id_users = ?", (str(ch_one_to_two), str(user_bd_id)))
    connection.commit()

    # 1Обновляем чипс_ван
    cursor.execute("UPDATE stat_chips SET chips_one = ? WHERE id_users = ?", (str(ch_curr_to_one), str(user_bd_id)))
    connection.commit()

    # 4Получение чипс_фор из БД
    cursor.execute("SELECT chips_three FROM stat_chips WHERE id_users = ?", (str(user_bd_id),))
    result_chips_three_to_fourth = cursor.fetchall()
    ch_three_to_fourth = result_chips_three_to_fourth[0][0]
    connection.commit()

    # Обновляем чипс_три
    connection.commit()
    cursor.execute("UPDATE stat_chips SET chips_three = ? WHERE id_users = ?", (str(ch_two_to_three), str(user_bd_id)))
    connection.commit()

    # # Обновляем чипс_фор
    cursor.execute("UPDATE stat_chips SET chips_fourth = ? WHERE id_users = ?", (str(ch_three_to_fourth),
                                                                                 str(user_bd_id)))
    connection.commit()

    connection.close()
    bot.send_message(message.chat.id, f'Текущее количество фишек - <code>{user_chips}</code> !', parse_mode="HTML")


@bot.message_handler(commands=['info'])
def get_info(message):
    user_id = message.from_user.id

    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT username, chips FROM Users WHERE telegramId = ?", (user_id,))
    result = cursor.fetchall()
    for name, chips in result:
        bot.send_message(message.chat.id,
            f'Приветствую, <strong>{name} !</strong>\n Количество твоих фишек = <code>{chips}</code> .',
                         parse_mode="HTML")
    connection.commit()
    connection.close()


@bot.message_handler(commands=['stats'])
def get_stats(message):
    user_id = message.from_user.id
    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM Users WHERE telegramId = ?", (user_id,))
    result_id = cursor.fetchall()
    user_bd_id = result_id[0][0]
    cursor.execute("SELECT chips_one, chips_two, chips_three, chips_fourth FROM stat_chips WHERE id_users = ?",
                   (user_bd_id,))
    result_chips = cursor.fetchall()
    connection.commit()
    connection.close()
    if result_chips[0][3] != None:
        for chips_o, chips_tw, chips_th, chips_f in result_chips:
            diff_one = chips_o - chips_tw
            diff_two = chips_th - chips_f
            bot.send_message(message.chat.id,
                f' {message.from_user.first_name}, разница фишек между первой <code>{str(chips_o)}</code> и второй '
                f' <code>{str(chips_tw)}</code> игрой составляет : <code>{str(diff_one)}</code>.\n'
                f' Разница фишек между третьей <code>{str(chips_th)}</code> и четвертой '
                f' <code>{str(chips_f)}</code> игрой составляет : <code>{str(diff_two)}</code>', parse_mode="HTML")
    else:
        bot.send_message(message.chat.id,
         f'{message.from_user.first_name}, введите <code> /setChips </code> минимум 4 раза, чтобы узнать статистику.',
         parse_mode="HTML")


@bot.message_handler(commands=['top'])
def get_top(message):
    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT userName, chips FROM Users")
    result = cursor.fetchall()
    for name, chips in nlargest(3, result, key=itemgetter(1)):
        bot.send_message(message.chat.id, f'Имя - {name}, фишки - <code>{chips}</code>', parse_mode="HTML")
    connection.commit()
    connection.close()


@bot.message_handler(content_types=['text'])
def use_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, пожалуйста, воспользутесь кнопками')


bot.infinity_polling()
