
# Create a table to store user information
createuserstable = '''
CREATE TABLE IF NOT EXISTS botusers
([chat_id] INTEGER PRIMARY KEY, [username] TEXT)
'''

# Create a table to store Group information
creategroupstable = '''
CREATE TABLE IF NOT EXISTS botgroups
([id] INTEGER PRIMARY KEY ,[groupid] BIGINT UNIQUE, [name] TEXT, [link] TEXT)
'''

countgroups = 'SELECT COUNT(*) FROM botgroups'

unknownusercmd = '''Я тебя не понял. Доступные команды:
        /start - перезапуск бота
        /kursmir - показать текущий обменный курс'''

unknownadmincmd = '''Я тебя не понял. Доступные команды:
        /start - перезапуск бота
        /kursmir - показать текущий обменный курс
        /admin - Администрирование бота'''

addgroup = 'INSERT OR IGNORE INTO "botgroups" ("groupid", "name", "link") VALUES("{}", "{}", "{}");'

addgrouphint = '''Чтобы добавить НОВУЮ группу, отправь 
    данные по маске: -ID, Название группы , @группы или ссылка'''

removegroup = 'DELETE FROM botgroups WHERE groupid="{}";'

removegrouphint = 'Чтобы УДАЛИТЬ группу, отправь ID группы'

addusertodb = 'INSERT OR IGNORE INTO "botusers" ("chat_id", "username") VALUES("{}", "{}");'

getlastrate = 'SELECT * FROM exrates WHERE id=(select max(id) from exrates) ORDER BY id DESC LIMIT 1'

starttext = '''Привет!
Функционал бота:

✅ По запросу выдает актуальный курс МИР.
✅ Автоматически присылает уведомления об изменении курса.
✅ Показывает в большую или меньшую сторону изменился курс.
✅ Может работать как в ЛС, так и в приватных/публичных группах.

Чтобы начать работу с ботом, нажмите /kursmir'''


starttextuser = '''Привет!
Функционал бота:

✅ По запросу выдает актуальный курс МИР.
✅ Автоматически присылает уведомления об изменении курса.
✅ Показывает в большую или меньшую сторону изменился курс.
✅ Может работать как в ЛС, так и в приватных/публичных группах.

Чтобы начать работу с ботом, нажмите /kursmir

*ЗДЕСЬ МОГЛА БЫТЬ ВАША РЕКЛАМА. ПИСАТЬ @pycarrot2*
'''

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
4400 4301 0402 9738 - Kaspi, Bakhti B.
5395 4574 1465 0022 - Jusan, Bakhti B.
TON: UQDMwwUaQeJponB_ngIXF99PM5Ktwwf-UDItbFDkdCO3OPCL
️'''

noaccesstext = '''
У данной группы нет доступа к этому боту,
Если вы считаете, что это ошибка,
пожалуйста, сообщите Ваш ID {} администратору боту: @pycarrot2.
Доступ для чатов платный - 2000 тг/мес
'''
