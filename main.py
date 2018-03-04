from telegram.ext import Updater, MessageHandler, Filters
import datetime
import sqlite3
from token_oks import API
from dateutil.parser import parse


def save_file(text):
    date = datetime.datetime.now().date()
    with open('{}.txt'.format(date), 'a') as f:
        f.write(text + ' - ' + str(datetime.datetime.now().strftime('%D, %H:%M')) + '\n')


def add_to_table(chat_id, user):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    item = [chat_id, '{}'.format(user['first_name']), '{}'.format(user['username']), 0]

    sql = '''INSERT INTO main (id, name, username, status) VALUES('{}', '{}', '{}', '{}')'''.format(
        str(item[0]),
        str(item[1]),
        str(item[2]),
        str(item[3]))

    cursor.execute(sql)
    conn.commit()
    conn.close()
    text = '{} добавлен в базу данных'.format(item[1])
    save_file(text)


def read_in_db():
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM main').fetchall()
    conn.close()
    return table


def check_in_db(chat_id, user):
    tables = read_in_db()
    ids = [i[0] for i in tables]

    if chat_id in ids:
        pass
    else:
        add_to_table(chat_id, user)


def update_sql_away(chat_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE main SET status = \'1\' WHERE id = \'{}\''.format(chat_id))
    conn.commit()
    cursor.execute('UPDATE main SET date = \'{}\' WHERE id = \'{}\''.format(datetime.datetime.now(), chat_id))
    conn.commit()
    # print(chat_id)
    conn.close()


def update_sql_come(chat_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE main SET status = \'0\' WHERE id = \'{}\''.format(chat_id))
    conn.commit()
    # print(chat_id)
    time = cursor.execute('SELECT * FROM main WHERE id =\'{}\''.format(chat_id)).fetchall()
    conn.close()

    return time[0][-1]


def get_statuses():
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM main WHERE status =\'1\'').fetchall()
    conn.close()
    return len(table)


def get_status(chat_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM main WHERE status =\'1\' AND id =\'{}\''.format(chat_id)).fetchall()
    conn.close()
    return bool(table)


def get_name(chat_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM main WHERE id =\'{}\''.format(chat_id)).fetchall()
    conn.close()
    return table


def textMessage(bot, update):
    message = update.message.text
    chat_id = update.message.chat_id
    user = bot.getChat(update.message.chat_id)
    check_in_db(chat_id, user)
    get_status(chat_id)
    if 'ушел' in message.lower():
        now_away = get_statuses()
        if get_status(chat_id):
            text = 'Ты и так уже отсутствуешь'
            text_save = u'{} попробовал уйти,когда и так уже отсутствовал'.format(user['first_name'])
            save_file(text_save)
            bot.send_message(chat_id=update.message.chat_id, text=text)

        elif now_away >= 3:
            text_save = u'{} попробовал уйти,когда 3-е отстутствуют'.format(user['first_name'])
            save_file(text_save)
            text = '3-ое уже отсутствуют'
            bot.send_message(chat_id=update.message.chat_id, text=text)
        else:
            text_save = u'{} ушел'.format(user['first_name'])
            save_file(text_save)
            # name = get_name(chat_id)[0][1]
            text = 'Ты ушел'
            update_sql_away(chat_id)
            bot.send_message(chat_id=update.message.chat_id, text=text)
    elif 'пришел' in message.lower():
        away_time = datetime.datetime.now() - parse(update_sql_come(chat_id))
        away_time_formated = away_time.seconds
        minutes = away_time_formated//60

        text_save = u'{} вернулся(отсутствовал - {})'.format(user['first_name'], away_time)
        save_file(text_save)
        text = 'Ты пришел, тебя не было {} минут'.format(minutes)
        bot.send_message(chat_id=update.message.chat_id, text=text)


def main():
    token = API
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    text_message_handler = MessageHandler(Filters.text, textMessage)
    dispatcher.add_handler(text_message_handler)
    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
