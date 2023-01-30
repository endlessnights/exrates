import json
import locale
import sqlite3
from datetime import date, datetime
import telebot
import time

# api_token = '5956191624:AAHw268WZP_apCbj9aDUc6wAFE9uyEd4B0o' # test bot @test239botbot
api_token = '6173204610:AAEVmFTmk-b3-UdjlUqHFyyFvVbI6va6Ymg'  # production bot @mirexratebot
bot = telebot.TeleBot(api_token)


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
Курс от {} - {} тенге за 1 руб'''.format(curdate, ratedate, rate)
    result2 = '''Сегодня {}'''.format(curdate)
    return result, result2


# Белый список пользователей и чатов, которые могут пользоваться ботом
with open("whitelist.txt", "r") as fwl:
    whiteliststr = str(fwl.read())
    whitelist = json.loads(whiteliststr)


@bot.message_handler(commands=['start'])
def hellouser(message):
    bot.send_message(message.chat.id, text='''Привет!
Функционал бота:

✅ По запросу выдает актуальный курс МИР.
✅ Если курс изменился, автоматически присылает уведомление с новым курсом.
✅ Показывает в большую или меньшую сторону изменился курс.
✅ Может работать как в ЛС, так и в приватных/публичных группах.

Доступ к боту платный: 100 тг/мес за пользователя, 2000 тг/мес для группы.
Чтобы начать работу с ботом, нажмите /kursmir''')


@bot.message_handler(commands=['kursmir'])
def mirexrate(message):
    user = message.chat.id
    result = getmirkurs()
    a, b = result
    if user in whitelist:
        bot.send_message(message.chat.id, text=a)
    else:
        print(whitelist)
        bot.send_message(message.chat.id, text='''У вас нет доступа к этому боту, 
Если вы считаете, что это ошибка, 
пожалуйста, сообщите Ваш ID {} администратору боту: @pycarrot2.'''.format(user))


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

with open("linecount.txt", "r") as f:
    previous_record_count = int(f.read())
with open("exrate.txt", "r") as frate:  # test
    previous_rate = float(frate.read())  # test
if current_record_count > previous_record_count:
    print("New database entry added")
    c, d = getmirkurs()
    print('D:', d)
    for chat in whitelist:
        if rate > previous_rate:  # test
            bot.send_message(chat_id=chat, text='''Новый обменный курс МИР!
{}
🔺{} тенге за 1 руб'''.format(d, rate))  # test
        else:  # test
            bot.send_message(chat_id=chat, text='''Новый обменный курс МИР!
{}
🔻{} тенге за 1 руб'''.format(d, rate))  # test
    with open("linecount.txt", "w") as f:
        f.write(str(current_record_count))
    with open("exrate.txt", "w") as frate:  # test
        frate.write(str(rate))  # test

bot.polling(none_stop=True)
