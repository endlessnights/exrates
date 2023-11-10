import random
import sqlite3
from datetime import date, datetime
from flask import render_template
from flask import Flask
import config
import requests

app = Flask(__name__)

conn = sqlite3.connect('ratesdb')
c = conn.cursor()
# Создаем базу данных, если еще не создана
c.execute('''
            CREATE TABLE IF NOT EXISTS exrates
            ([id] INTEGER PRIMARY KEY, [date] DATE, [rate] DOUBLE, [exrate] FLOAT)
            ''')
conn.commit()

def get_kurs_from_web():
    url = "https://i.dvcdn.ru/rates/mir.json"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        for entry in data:
            if entry['currency'] == 'Казахстанский\xa0тенге':
                rate = entry['rate']
                rate = rate.replace(',', '.')
                return rate

rate = get_kurs_from_web()
print(rate)
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
    random_ad_text = random.choice(config.web_ad_texts)
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
        random_ad_text=random_ad_text,
    )


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")