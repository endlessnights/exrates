import sqlite3
from datetime import date, datetime
import requests as requests
from pyquery import PyQuery as pq
from flask import render_template
from flask import Flask
import json

app = Flask(__name__)

conn = sqlite3.connect('ratesdb')
c = conn.cursor()
# Создаем базу данных, если еще не создана
c.execute('''
            CREATE TABLE IF NOT EXISTS exrates
            ([id] INTEGER PRIMARY KEY, [date] DATE, [rate] DOUBLE, [exrate] FLOAT)
            ''')
conn.commit()

uri = 'https://mironline.ru/support/list/kursy_mir/'
resp = requests.get(uri, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
print(resp)
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
    sqlexec = 'SELECT EXISTS(SELECT * FROM exrates WHERE id=(select max(id) from exrates) and exrate={} ORDER BY id DESC LIMIT 1)'
    presence = (c.execute(sqlexec.format(exrate))).fetchone()
    print(presence)
    # Если не совпадает, записываем новое значение
    if str(presence) == '(0,)':
        status = 'Курс изменился'
        print(status)
        conn = sqlite3.connect('ratesdb')
        c = conn.cursor()
        c.execute(
            'INSERT INTO "exrates" ("date", "rate", "exrate") VALUES("{}", "{}", "{}");'.format(
                cdate, rate, exrate))
        conn.commit()
        conn.close()
    else:
        status = 'Курс не изменился'
        print(status)


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


@app.route("/")
def exrates(*args):
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
        rate=rate,
        presence=presence,
        status=status,
        uri=uri,
        resp=resp,
    )


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")