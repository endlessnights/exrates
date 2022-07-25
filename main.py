import sqlite3
from datetime import date, datetime
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
    cdate = str(date.today())
    print(cdate)
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
                cdate, rate, exrate))
        conn.commit()
        conn.close()

app = Flask(__name__)


def getdata(rows):
    conn = sqlite3.connect('ratesdb')
    c = conn.cursor()
    c.execute('SELECT date,exrate FROM exrates')
    # получаем данные из таблицы БД в dict
    columns = [col[0] for col in c.description]
    rows = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.commit()
    conn.close()
    return rows


@app.route('/')
def exratesview(*args):
    rows = getdata(rows=args)
    tdate = str(date.today().strftime("%d.%m.%Y"))

    def format_datetime(value, format="%d-%m-%Y"):
        if value is None:
            return ""
        return datetime.strptime(value, "%Y-%m-%d").strftime(format)

    # configured Jinja2 environment with user defined
    app.jinja_env.filters['date_format'] = format_datetime
    return render_template(
        'index.html',
        rows=rows,
        tdate=tdate,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)


@app.route('/json')
def getjsondata(*args):
    rows = getdata(rows=args)
    json_string = json.dumps(rows)
    return render_template(
        'source.json',
        json_string=json_string,
    )

#
# @app.route('/list')
# def getlistdata(*args):
#     rows = getdata(rows=args)
#     return render_template(
#         'list.txt',
#         rows=rows,
#     )
