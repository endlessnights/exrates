import sqlite3
from datetime import date
import requests as requests
from pip._internal.network.utils import HEADERS
from pyquery import PyQuery as pq
from flask import render_template
from flask import Flask
import json

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
    exrate = round((1 / float(rate)), 2)
    print('Обменный курс: ' + str(exrate))
    # Проверяем совпадает ли последняя запись с текущим курсом
    presence = (c.execute('SELECT EXISTS(SELECT * FROM exrates WHERE exrate = {} LIMIT 1)'.format(exrate))).fetchone()
    print(presence)
    # Если не совпадает, записываем новое значение
    if str(presence) == '(0,)':
        print('True')
        conn = sqlite3.connect('ratesdb')
        c = conn.cursor()
        c.execute(
            'INSERT INTO "exrates" ("date", "rate", "exrate") VALUES("{}", "{}", "{}");'.format(
                date, rate, exrate))
        conn.commit()
        conn.close()

app = Flask(__name__)
app.testing = True


@app.route('/')
def exratesview():
    conn = sqlite3.connect('ratesdb')
    c = conn.cursor()
    c.execute('SELECT date,exrate FROM exrates')
    columns = [col[0] for col in c.description]
    rows = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return render_template(
        'index.html',
        title="ExRates PS MIR",
        rows=rows)


if __name__ == '__main__':
    app.run()
