from telegram.ext import Updater, MessageHandler, Filters
import datetime
import sqlite3
from token_oks import API
from dateutil.parser import parse
from ast import literal_eval


def save_file(text, user=False):

    if user:
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        cursor.execute('UPDATE reset SET name = \'{}_{}_{}\''.format(user,
                                                                     datetime.datetime.now().date(),
                                                                     datetime.datetime.now().time()))
        conn.commit()
        conn.close()

    else:
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        table = cursor.execute('SELECT * FROM reset').fetchall()
        conn.close()
        table = str(table[0][0]).replace('-', '_').replace(':', ('_')).split('.')[0]

        with open('{}.txt'.format(table), 'a') as f:
            f.write(text + ', ' + str(datetime.datetime.now().strftime('%D, %H:%M')) + '\n')


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
    conn.close()


def update_sql_come(chat_id):
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE main SET status = \'0\' WHERE id = \'{}\''.format(chat_id))
    conn.commit()
    time = cursor.execute('SELECT * FROM main WHERE id =\'{}\''.format(chat_id)).fetchall()
    cursor.execute('UPDATE main SET date = \'NULL\' WHERE id = \'{}\''.format(chat_id))
    conn.commit()
    conn.close()

    return time[0][-1]


def get_statuses():
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM main WHERE status =\'1\'').fetchall()
    conn.close()
    return len(table)


def get_who_away():
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM main WHERE status =\'1\'').fetchall()
    conn.close()
    users = [i[1] for i in table]
    return users


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


def get_away_time():
    logs = []
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    table = cursor.execute('SELECT * FROM reset').fetchall()
    conn.close()
    table = str(table[0][0]).replace('-', '_').replace(':', ('_')).split('.')[0]
    with open('{}.txt'.format(table), 'r') as f:
        for i in f:
            logs.append(i)
    return logs


def update_sql_all_come():
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE main SET status = \'0\'')
    conn.commit()
    conn.close()


def textMessage(bot, update):
    message = update.message.text

    chat_id = str(update)
    chat_id = literal_eval(chat_id)['message']['from']['id']
    user = bot.getChat(chat_id)
    check_in_db(chat_id, user)
    get_status(chat_id)
    text_away = ['ушел', 'ушла', 'убыл', 'убыла', 'ушёл', 'ушол', 'вышел', 'вышла']
    text_come = ['пришел', 'пришла', 'прибыл', 'прибыла', 'пришёл', 'пришол']

    adm_ids = [256737675, 429070522, 416966362, 432725291, 166998097, 420588132, 290908902, 421223508]
    if bool(list(set(text_away) & set(message.lower().split(' ')))):
        now_away = get_statuses()
        if get_status(chat_id):
            text = 'Ты и так уже отсутствуешь'
            text_save = u'{}, попробовал уйти когда и так уже отсутствовал'.format(user['first_name'])
            save_file(text_save)
            bot.send_message(chat_id=update.message.chat_id, text=text)

        elif now_away >= 3:
            text_save = u'{}, попробовал уйти когда 3-е отстутствуют'.format(user['first_name'])
            save_file(text_save)
            text = '3-ое уже отсутствуют'
            bot.send_message(chat_id=update.message.chat_id, text=text)

        else:
            text_save = u'{}, ушел'.format(user['first_name'])
            save_file(text_save)
            # name = get_name(chat_id)[0][1]
            text = '{} ушел(а)'.format(user['first_name'])
            update_sql_away(chat_id)
            bot.send_message(chat_id=update.message.chat_id, text=text)
    elif 'кто отсутствует' in message.lower() and chat_id in adm_ids:

        users = ', '.join(get_who_away())
        text = 'Сейча отсутствуют - {}'.format(users)
        bot.send_message(chat_id=update.message.chat_id, text=text)

    elif 'кто сколько отсутствовал' in message.lower() and chat_id in adm_ids:
        logs = get_away_time()
        d = {}
        for i in logs:
            if 'добавлен' in i:
                pass
            else:
                d[i.split(',')[0]] = 0
        for i in logs:
            if 'отсутствовал' in i:
                time = int(i.split(':')[1])
                d[i.split(',')[0]] += time
        names = [i for i in d]
        for i in names:
            text = '{} отсутствовал(а) {} мин.'.format(i, d[i])
            bot.send_message(chat_id=update.message.chat_id, text=text)

    elif bool(list(set(text_come) & set(message.lower().split(' ')))):

        if not get_status(chat_id):
            text = 'Ты и так еще не ушел(а)'
            text_save = u'{}, попробовал прийти пока не ушел'.format(user['first_name'])
            save_file(text_save)
            bot.send_message(chat_id=update.message.chat_id, text=text)

        else:
            away_time = datetime.datetime.now() - parse(update_sql_come(chat_id))
            away_time_formated = away_time.seconds
            minutes = away_time_formated // 60

            text_save = u'{}, вернулся (отсутствовал - {})'.format(user['first_name'], away_time)
            save_file(text_save)
            text = '{} пришел(а), его(её) не было {} мин.'.format(user['first_name'], minutes)
            bot.send_message(chat_id=update.message.chat_id, text=text)

    elif 'reset' in message.lower() and chat_id in adm_ids:
        text_save = u'{}, restarted logs)'.format(user['first_name'])
        save_file(text_save, user=user['first_name'])
        update_sql_all_come()
        text = 'Reset completed'
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
