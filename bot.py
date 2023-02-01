import json
import locale
import sqlite3
from datetime import date, datetime
import telebot
from telebot import types
import time

api_token = '5956191624:AAHw268WZP_apCbj9aDUc6wAFE9uyEd4B0o'  # test bot @test239botbot
# api_token = '6173204610:AAEVmFTmk-b3-UdjlUqHFyyFvVbI6va6Ymg'  # production bot @mirexratebot
bot = telebot.TeleBot(api_token)
users = []

# Connect to the database
conn = sqlite3.connect('botusers.db')
c = conn.cursor()
# Create a table to store user information
c.execute('''
            CREATE TABLE IF NOT EXISTS botusers
            ([chat_id] INTEGER PRIMARY KEY, [username] TEXT)
            ''')
conn.commit()
conn.close()


def getmirkurs():
    conn = sqlite3.connect('ratesdb')
    c = conn.cursor()
    c.execute('SELECT * FROM exrates WHERE id=(select max(id) from exrates) ORDER BY id DESC LIMIT 1')
    records = c.fetchall()
    columns = [col[0] for col in c.description]
    rows = [dict(zip(columns, row)) for row in c.fetchall()]
    for row in records:
        ratedate = row[1]
        rate = row[3]
    c.close()
    # Получаем дату курса и конвертируем в нормальный вид
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    ratedate = datetime.strptime(ratedate, '%Y-%m-%d')
    ratedate = datetime.strftime(ratedate, '%d %B %Y')
    # Получаем текущую дат и конвертируем в нормальный вид
    curdate = str(date.today())
    curdate = datetime.strptime(curdate, '%Y-%m-%d')
    curdate = datetime.strftime(curdate, '%d %B %Y')
    result = '''Сегодня {}
1 RUB = {} Тенге (Курс от {})'''.format(curdate, rate, ratedate)
    result2 = '''Сегодня {}'''.format(curdate)
    return result, result2


# Белый список пользователей и чатов, которые могут пользоваться ботом
with open("whitelist.txt", "r") as fwl:
    whiteliststr = str(fwl.read())
    whitelist = json.loads(whiteliststr)


def getusersfromdb():
    conn = sqlite3.connect('botusers.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM botusers')
    chat_ids = [chat_id[0] for chat_id in c.fetchall()]
    conn.close()

    return chat_ids


starttext = '''Привет!
Функционал бота:
    
✅ По запросу выдает актуальный курс МИР.
✅ Автоматически присылает уведомления об изменении курса.
✅ Показывает в большую или меньшую сторону изменился курс.
✅ Может работать как в ЛС, так и в приватных/публичных группах.

Чтобы начать работу с ботом, нажмите /kursmir'''


@bot.message_handler(commands=['start'])
def hellouser(message):
    currentuser = message.chat.id
    userinfo = message.from_user
    # user_info = (message.chat.id, message.chat.username, currentuser.first_name, currentuser.last_name)
    if not str(currentuser).startswith('-'):
        conn = sqlite3.connect('botusers.db')
        c = conn.cursor()
        c.execute(
            'INSERT OR IGNORE INTO "botusers" ("chat_id", "username") VALUES("{}", "{}");'.format(userinfo.id,
                                                                                                  userinfo.username))
        conn.commit()
        conn.close()
    chat_ids = getusersfromdb()
    currentuser = message.chat.id
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='💰 Поддержать автора и проект', callback_data='send_message')
    markup.add(button)
    if str(currentuser).startswith('-'):
        bot.send_message(chat_id=message.chat.id, text=starttext)
    else:
        bot.send_message(message.chat.id, text=starttext, reply_markup=markup)


supporttext = '''
Привет! Меня зовут Бахти Б. @pycarrot2 и 
Вы можете поддержать меня и мои проекты, о которых вы возможно слышали:
❇️ Данный бот обменного курса МИР тенге-руб
❇️ Сайт exrates.geekcv.io
❇️ Сайт-портал MeetKZ.com
❇️ Сайты, ранее актуальные в период мобилизации:
1. kpp.geekcv.io
2. bnb.geekcv.io
❇️ Бот выдачи настроек VPN @Vas3kVPNbot

Реквизиты:
+7 705 568 50 30 Kaspi (Bakhti B.)

️'''


@bot.callback_query_handler(func=lambda c: c.data == 'send_message')
def callback_handler(callback_query):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(chat_id=callback_query.message.chat.id, text=supporttext)


@bot.message_handler(commands=['kursmir'])
def mirexrate(message):
    user = message.chat.id  # Текущий ID чата/пользователя
    result = getmirkurs()
    a, b = result
    if str(user).startswith('-'):  # проверяем, если текущий пользователь - чат/группа
        if user in whitelist:  # и -ID чата/группы есть в списке
            bot.send_message(message.chat.id, text=a)
        else:
            bot.send_message(message.chat.id, text='''У данного нет доступа к этому боту,
Если вы считаете, что это ошибка,
пожалуйста, сообщите Ваш ID {} администратору боту: @pycarrot2.
Доступ для чатов платный - 2000 тг/мес'''.format(user))
    else:
        bot.send_message(message.chat.id, text=a)  # если текущий пользователь - человек, отправляем ответ
        userinfo = message.from_user
        conn = sqlite3.connect('botusers.db')
        c = conn.cursor()
        c.execute(
            'INSERT OR IGNORE INTO "botusers" ("chat_id", "username") VALUES("{}", "{}");'.format(userinfo.id,
                                                                                                  userinfo.username))
        conn.commit()
        conn.close()
    return user


conn = sqlite3.connect('ratesdb')
c = conn.cursor()
c.execute('SELECT * FROM exrates WHERE id=(select max(id) from exrates) ORDER BY id DESC LIMIT 1')
records = c.fetchall()
columns = [col[0] for col in c.description]
rows = [dict(zip(columns, row)) for row in c.fetchall()]
for row in records:
    ratedate = row[1]
    rate = row[3]
c.execute("SELECT COUNT(*) FROM exrates")
current_record_count = c.fetchone()[0]
print(current_record_count)
c.close()


def send_message_to_chats(text, chats, chat_ids):
    for chat in chats:
        bot.send_message(chat_id=chat, text=text)
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=text)


def write_to_file(filename, data):
    with open(filename, "w") as f:
        f.write(str(data))


def read_from_file(filename):
    with open(filename, "r") as f:
        return float(f.read())


def main():
    previous_record_count = read_from_file("linecount.txt")
    previous_rate = read_from_file("exrate.txt")
    if current_record_count > previous_record_count:
        print("New database entry added")
        c, d = getmirkurs()
        chat_ids = getusersfromdb()
        rate_prefix = "🔺" if rate > previous_rate else "🔻"
        message = f"Новый обменный курс МИР!\n{d}\n{rate_prefix}{rate} тенге за 1 руб"
        send_message_to_chats(message, whitelist, chat_ids)
        write_to_file("linecount.txt", current_record_count)
        write_to_file("exrate.txt", rate)


if __name__ == "__main__":
    main()

bot.polling(none_stop=True)
