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
    bot.send_message(message.chat.id, f'Приветствую, <strong> {user_name} !</strong>\n Бот создан для хранения'
                                      f' информации о фишках. Пожалуйста, пользуйтесь исключительно кнопками',
                     parse_mode="HTML", reply_markup=markup)

    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    if not result:
        connection = sqlite3.connect(configuration.database)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (telegram_id,username,chips) VALUES (?, ?, ?)', (user_id, user_name, 0))

        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
        result_id = cursor.fetchall()
        user_bd_id = result_id[0][0]
        cursor.execute(
            'INSERT INTO stat_chips (id_users, chips_one, chips_two, chips_three, chips_fourth) VALUES (?, ?, ?, ?, ?)',
            (user_bd_id, 0, 0, 0, 0))
        connection.commit()
        connection.close()
    else:
        bot.send_message(message.chat.id, f'<u> <b> Вы уже зарегистрированы ! </b> </u>', parse_mode="HTML")


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
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
    result_id = cursor.fetchall()
    user_bd_id = result_id[0][0]
    connection.commit()

    # 0Получение текущего кол-ва фишек для присвоения в чипс_ван
    cursor.execute("SELECT chips FROM users WHERE id =?", (str(user_bd_id),))
    result_chips_curr_to_one = cursor.fetchall()
    ch_curr_to_one = result_chips_curr_to_one[0][0]
    connection.commit()

    # 0Обновляем текущие фишки
    cursor.execute("UPDATE users SET chips = ? WHERE telegram_id = ?", (user_chips, user_id))
    connection.commit()

    # 1Получение чипс_ван из БД
    cursor.execute("SELECT chips_one FROM stat_chips WHERE id_users = ?", (str(user_bd_id),))
    result_chips_one_to_two = cursor.fetchall()
    ch_one_to_two = result_chips_one_to_two[0][0]
    connection.commit()

    # 2Получение чипс_ту из БД
    cursor.execute("SELECT chips_two FROM stat_chips WHERE id_users = ?", (str(user_bd_id),))
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
    bot.send_message(message.chat.id, f'Текущее количество фишек <b>—</b> {user_chips} !', parse_mode="HTML")


@bot.message_handler(commands=['info'])
def get_info(message):
    user_id = message.from_user.id

    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT username, chips FROM users WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchall()
    for name, chips in result:
        bot.send_message(message.chat.id, f'<b>{name}, </b> количество Ваших фишек <b>—</b> {chips}.',
                         parse_mode="HTML")
    connection.commit()
    connection.close()


@bot.message_handler(commands=['stats'])
def get_stats(message):
    user_id = message.from_user.id
    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
    result_id = cursor.fetchall()
    user_bd_id = result_id[0][0]
    cursor.execute("SELECT chips_one, chips_two, chips_three, chips_fourth FROM stat_chips WHERE id_users = ?",
                   (user_bd_id,))
    result_chips = cursor.fetchall()
    connection.commit()
    connection.close()

    if result_chips[0][3] is not None:
        for chips_f, chips_th, chips_tw, chips_o in result_chips:
            diff_one = int(chips_f) - int(chips_th)
            diff_two = int(chips_tw) - int(chips_o)
            bot.send_message(message.chat.id, f'{message.from_user.first_name}, разница фишек между:\n'
                                              f'четвертой [<b>{str(chips_f)}</b>] и третьей [<b>{str(chips_th)}</b>]'
                                              f'игрой <b>—</b> <code>{str(diff_one)} </code>.\n'
                                              f'второй [<b>{str(chips_tw)}</b>] и первой [<b>{str(chips_o)}</b>] '
                                              f'игрой <b>—</b> <code> {str(diff_two)}</code>', parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, f'{message.from_user.first_name}, <u> введите </u> <code> /setChips </code> '
                                          f'<u>минимум 4 раза, чтобы узнать статистику. </u>', parse_mode="HTML")


@bot.message_handler(commands=['top'])
def get_top(message):
    connection = sqlite3.connect(configuration.database)
    cursor = connection.cursor()
    cursor.execute("SELECT username, chips FROM users")
    result = cursor.fetchall()
    for name, chips in nlargest(3, result, key=itemgetter(1)):
        bot.send_message(message.chat.id, f' {name} <b>—</b> {chips}', parse_mode="HTML")
    connection.commit()
    connection.close()


@bot.message_handler(content_types=['text'])
def use_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name}, <u> пожалуйста, воспользутесь кнопками </u>',
                     parse_mode="HTML")


bot.infinity_polling()
