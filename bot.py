import locale
import re
import sqlite3
import time
from datetime import date, datetime

import telebot
from telebot import types

import config
import func

api_token = '5956191624:AAHw268WZP_apCbj9aDUc6wAFE9uyEd4B0o'  # test bot @test239botbot
# api_token = '6173204610:AAEVmFTmk-b3-UdjlUqHFyyFvVbI6va6Ymg'  # production bot @mirexratebot
bot = telebot.TeleBot(api_token)
users = []

# Connect to the database
conn = sqlite3.connect('botusers.db')
c = conn.cursor()
# Create a table to store user information
c.execute(config.createuserstable)
conn.commit()
# Create a table to store Group information
c.execute(config.creategroupstable)
conn.commit()
conn.close()


def getmirkurs():
    conn = sqlite3.connect('ratesdb')
    c = conn.cursor()
    c.execute(config.getlastrate)
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


def getchatidsfromdb():
    conn = sqlite3.connect('botusers.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM botusers')
    user_ids = [chat_id[0] for chat_id in c.fetchall()]
    c.execute('SELECT groupid FROM botgroups')
    group_ids = [chat_id[0] for chat_id in c.fetchall()]
    conn.close()

    return user_ids, group_ids


@bot.message_handler(commands=['start'])
def hellouser(message):
    currentuser = message.chat.id
    userinfo = message.from_user
    if not str(currentuser).startswith('-'):
        conn = sqlite3.connect('botusers.db')
        c = conn.cursor()
        c.execute(config.addusertodb.format(userinfo.id, userinfo.username))
        conn.commit()
        conn.close()
    currentuser = message.chat.id
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='💰 Поддержать автора и проект', callback_data='send_message')
    markup.add(button)
    if str(currentuser).startswith('-'):
        bot.send_message(chat_id=message.chat.id, text=config.starttext)
    else:
        bot.send_message(message.chat.id, text=config.starttext, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'send_message')
def callback_handler(callback_query):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(chat_id=callback_query.message.chat.id, text=config.supporttext)


@bot.message_handler(commands=['kursmir'])
def mirexrate(message):
    user = message.chat.id  # Текущий ID чата/пользователя
    result = getmirkurs()
    a, b = result
    user_ids, group_ids = getchatidsfromdb()
    if str(user).startswith('-'):  # проверяем, если текущий пользователь - чат/группа
        if user in group_ids:  # и -ID чата/группы есть в списке
            try:
                bot.send_message(message.chat.id, text=a)
            except telebot.apihelper.ApiTelegramException as e:
                func.catcherrors(e, user)
        else:
            try:
                bot.send_message(message.chat.id, text=config.noaccesstext.format(user))
            except telebot.apihelper.ApiTelegramException as e:
                func.catcherrors(e, user)
    else:
        try:
            bot.send_message(message.chat.id, text=a)  # если текущий пользователь - человек, отправляем ответ
            userinfo = message.from_user
            conn = sqlite3.connect('botusers.db')
            c = conn.cursor()
            c.execute(config.addusertodb.format(userinfo.id, userinfo.username))
            conn.commit()
            conn.close()
        except telebot.apihelper.ApiTelegramException as e:
            func.catcherrors(e, user)
    return user


@bot.message_handler(func=lambda message: message.text and "/admin" not in message.text)
def handle_message(message):
    user = message.chat.id
    if not str(user).startswith('-'):   # Отвечать только пользователям в ЛС
        if not message.chat.id == adminuser:
            bot.reply_to(message, '''Я тебя не понял. Доступные команды:
        /start - перезапуск бота
        /kursmir - показать текущий обменный курс''')
        else:
            bot.reply_to(message, '''Я тебя не понял. Доступные команды:
        /start - перезапуск бота
        /kursmir - показать текущий обменный курс
        /admin - Администрирование бота''')
    else:
        print('It is group')


adminuser = 326070831


@bot.message_handler(commands=['admin'])
def admintools(message):
    if message.chat.id == adminuser:
        markup = types.InlineKeyboardMarkup()
        grouplistbtn = types.InlineKeyboardButton(text='📋 Список групп', callback_data='grouplist')
        statsbtn = types.InlineKeyboardButton(text='👥 Показать статистику', callback_data='showstats')
        addgroupbtn = types.InlineKeyboardButton(text='➕ Добавить группу', callback_data='addgroup')
        removegroupbtn = types.InlineKeyboardButton(text='➖ Удалить группу', callback_data='removegroup')
        markup.add(grouplistbtn)
        markup.add(addgroupbtn)
        markup.add(removegroupbtn)
        markup.add(statsbtn)
        bot.send_message(chat_id=adminuser, text='Администрирование бота', reply_markup=markup)


# Выводим список групп из белого списка и рисуем две кнопки - Добавить и удалить группы
@bot.callback_query_handler(func=lambda c: c.data == 'grouplist')
def callback_handler(callback_query):
    addgroupbtn = types.InlineKeyboardButton(text='Добавить группу', callback_data='addgroup')
    removegroupbtn = types.InlineKeyboardButton(text='Удалить группу', callback_data='removegroup')
    markup = types.InlineKeyboardMarkup()
    markup.add(addgroupbtn)
    markup.add(removegroupbtn)
    bot.answer_callback_query(callback_query.id)
    conn = sqlite3.connect('botusers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM botgroups')
    rows = c.fetchall()
    c.close()
    grouplist = ''
    gloopcount = 0
    for row in rows:
        pkid, gid, gname, glink = row
        gloopcount += 1
        grouplist += f"{gloopcount, gid, gname, glink}\n"
        time.sleep(0.05)
        patn = re.sub(r"[\([{})\]]", "", grouplist)
    bot.send_message(chat_id=callback_query.message.chat.id, text=patn, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'showstats')
def callback_handler(callback_query):
    conn = sqlite3.connect('botusers.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM botusers")
    userscount = c.fetchone()[0]
    time.sleep(0.25)
    c.execute("SELECT COUNT(*) FROM botgroups")
    groupscount = c.fetchone()[0]
    bot.send_message(chat_id=adminuser, text='''
Статистика бота:

👱‍ Кол-во пользователей: {}
👥 Кол-во групп: {}'''.format(userscount, groupscount))
    conn.commit()
    c.close()


# Получаем данные от админа для добавления новой группы
@bot.callback_query_handler(func=lambda c: c.data == 'addgroup')
def callback_handler(callback_query):
    addgroup = bot.send_message(chat_id=callback_query.message.chat.id, text='''Чтобы добавить НОВУЮ группу, отправь 
    данные по маске: -ID, Название группы , @группы или ссылка''')
    bot.register_next_step_handler(addgroup, groupadd)


# Получаем данные от админа для удаления группы
@bot.callback_query_handler(func=lambda c: c.data == 'removegroup')
def callback_handler(callback_query):
    removegroup = bot.send_message(chat_id=callback_query.message.chat.id, text='Чтобы УДАЛИТЬ группу, отправь ID '
                                                                                'группы')
    bot.register_next_step_handler(removegroup, groupremove)


# Добавление новой группы через кнопку
def groupadd(message):
    data = message.text
    try:
        newgid, newgname, newglink = data.split(',')
        conn = sqlite3.connect('botusers.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM botgroups")
        gcountold = c.fetchone()[0]
        time.sleep(0.25)
        c.execute((config.addgroup.format(newgid, newgname, newglink)))
        time.sleep(0.25)
        c.execute("SELECT COUNT(*) FROM botgroups")
        gcountcur = c.fetchone()[0]
        conn.commit()
        c.close()
        if gcountold != gcountcur:
            bot.send_message(chat_id=adminuser,
                             text='Добавлена новая группа {} с ID {} и ссылкой {}'.format(newgname, newgid, newglink))
        else:
            bot.send_message(chat_id=adminuser, text='Что-то пошло не так')
    except ValueError:
        print('Not enough values to unpack')
        bot.send_message(chat_id=adminuser, text='Недостаточно аргументов, должно быть 3')


def groupremove(message):
    data = message.text
    conn = sqlite3.connect('botusers.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM botgroups")
    time.sleep(0.25)
    gcountold = c.fetchone()[0]
    c.execute(config.removegroup.format(data))
    conn.commit()
    c.execute("SELECT COUNT(*) FROM botgroups")
    gcountcur = c.fetchone()[0]
    if gcountold > gcountcur:
        bot.send_message(chat_id=adminuser, text='Группа с ID {} успешно удалена'.format(data))
    else:
        bot.send_message(chat_id=adminuser, text='Что-то пошло не так')
    c.close()


conn = sqlite3.connect('ratesdb')
c = conn.cursor()
c.execute(config.getlastrate)
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
        user_ids, group_ids = getchatidsfromdb()
        rate_prefix = "🟢⬆️ " if rate > previous_rate else "🔴⬇️ "
        message = f"Новый обменный курс МИР!\n{d}\n{rate_prefix}{rate} тенге за 1 руб"
        for chat in group_ids + user_ids:
            try:
                bot.send_message(chat_id=chat, text=message)
            except telebot.apihelper.ApiTelegramException as e:
                func.catcherrors(e, chat)
            time.sleep(2)
        write_to_file("linecount.txt", current_record_count)
        write_to_file("exrate.txt", rate)


if __name__ == "__main__":
    main()

bot.polling(none_stop=True)
