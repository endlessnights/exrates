import json
import locale
import sqlite3
from datetime import date, datetime

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
ratedate = datetime.strptime(ratedate, '%Y-%m-%d')
ratedate = datetime.strftime(ratedate, '%d %B %Y')
# Получаем текущую дат и конвертируем в нормальный вид
cdate = str(date.today())
cdate = datetime.strptime(cdate, '%Y-%m-%d')
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
cdate = datetime.strftime(cdate, '%d %B %Y')
print('Сегодня {}'.format(cdate))
print('Курс от {} - {} тенге за 1 руб'.format(ratedate, rate))
print('Автор бота: @pycarrot2')
