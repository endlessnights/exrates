
# Create a table to store user information
createuserstable = '''
CREATE TABLE IF NOT EXISTS botusers
([chat_id] INTEGER PRIMARY KEY, [username] TEXT)
'''

# Create a table to store Group information
creategroupstable = '''
CREATE TABLE IF NOT EXISTS botgroups
([id] INTEGER PRIMARY KEY ,[groupid] BIGINT, [name] TEXT, [link] TEXT)
'''

addusertodb = 'INSERT OR IGNORE INTO "botusers" ("chat_id", "username") VALUES("{}", "{}");'

getlastrate = 'SELECT * FROM exrates WHERE id=(select max(id) from exrates) ORDER BY id DESC LIMIT 1'

starttext = '''Привет!
Функционал бота:

✅ По запросу выдает актуальный курс МИР.
✅ Автоматически присылает уведомления об изменении курса.
✅ Показывает в большую или меньшую сторону изменился курс.
✅ Может работать как в ЛС, так и в приватных/публичных группах.

Чтобы начать работу с ботом, нажмите /kursmir
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
2200 1502 3169 8355 - Альфа-Банк МИР (РФ)
4584 4328 4064 9595 - Альфа-Банк (РФ)
️'''

noaccesstext = '''
У данного нет доступа к этому боту,
Если вы считаете, что это ошибка,
пожалуйста, сообщите Ваш ID {} администратору боту: @pycarrot2.
Доступ для чатов платный - 2000 тг/мес
'''
