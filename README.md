# Бот оповещения через ТГ #

Бот для рассылки оповещений о балансе Frigate в Телеграм-чаты.

Для запуска необходимо установить зависимости из `requirements.txt`, а также указать переменные окружения:
```
TG_API_ID=<Идентификатор приложения>
TG_API_HASH=<Хэш идентификатора приложения>
TG_BOT_TOKEN=<токен Телеграм-бота>
FRIGAT_API_KEY=<Ключ доступа к API Frigate>
```
Чтобы получить идентификатор приложения и его хэш, нужно пройти по адресу [https://my.telegram.org](https://my.telegram.org), залогиниться и создать приложение. В поле "Device" необходимо указать desktop (по крайней мере на данный момент).

Если бот не реагирует на сообщения в группах, необходимо разрешить ему доступ к сообщениям. Это можно сделать командой /setprivacy через @BotFather.

Для запуска бота необходим доступ к API Bot manager, от которого бот получает настройки лимитов, данные об авторизованных Телеграм-чатах и историю баланса.

В настоящий момент бот запускается командой: `/start`, которой в интерфейс добавляется кнопка "Баланс Фригат Прокси", при нажатии на которую в чат публикуется сообщение с балансом Frigate.
Если при нажатии на кнопку бот отвечает сообщением "У вас нет доступа к этой информации", это означает, что чат, в котором произведен запрос, не авторизован. Для авторизации id чата необходимо 
добавить в "ТГ Группы" в интерфейсе админа в Bot manager.

Помимо предоставления информации по запросу, бот рассылает уведомления о состоянии баланса в отмеченные чаты. О добавлении чата в рассылку подробнее сказано в README Bot manager.
Значения баланса, ниже которых бот начинает рассылать уведомление о необходимости оплаты, указываются в настройках бота в Bot manager. Там же указываются временные интервалы, 
через которые бот отправляет уведомления. Подробнее об этом говорится в README Bot manager.

При первом запуске приложения потребуется ввести код подтверждения логина. Запрос на ввод кода появится в консоли.

Создать докер образ можно командой `docker build -f Dockerfile -t <имя образа> .`, если у вас консольный клиент. Запустить контейнер можно следующим образом:
```
docker run --name <название контейнера> -e 'TG_API_ID=<значение>' -e 'TG_API_HASH=<значение>' -e 'TG_BOT_TOKEN=<значение>' -it --net=host balance_bot:latest
```
Когда бот будет запущен и авторизован, можно отключиться от контейнера без его остановки, нажав Ctrl-P, затем Ctrl-Q.
