import sqlite3
from datetime import date
import requests as requests
from pip._internal.network.utils import HEADERS
from pyquery import PyQuery as pq


conn = sqlite3.connect('ratesdb')
c = conn.cursor()
# Создаем базу данных, если еще не создана
c.execute('''
            CREATE TABLE IF NOT EXISTS exrates
            ([id] INTEGER PRIMARY KEY, [date] DATE, [rate] DOUBLE, [exrate] FLOAT)
            ''')
conn.commit()

uri = 'https://mironline.ru/support/list/kursy_mir/'
resp = requests.get(uri, headers=HEADERS)
if not resp.ok:
    pass
else:
    d = pq(resp.text)
    rate = d("td:contains('Казахстанский тенге')").parent().find("span").text().replace(',', '.')
    # получаем текущую дату гггг-мм-дд
    date = str(date.today())
    print('Курс: ' + str(rate))
    # получаем обменный курс
    exrate = round((1/float(rate)), 2)
    print('Обменный курс: ' + str(exrate))
    conn = sqlite3.connect('ratesdb')
    c = conn.cursor()
    c.execute(
        'INSERT INTO "exrates" ("date", "rate", "exrate") VALUES("{}", "{}", "{}");'.format(
            date, rate, exrate))
    conn.commit()
    conn.close()
