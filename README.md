# Бот оповещения через ТГ #

Прототип бота для рассылки оповещений о балансе в Телеграм.

Для запуска необходимо установить зависимости из `requirements.txt`, а также указать переменные окружения:

```
TG_API_ID=Идентификатор приложения
TG_API_HASH=Хэш идентификатора приложения
TG_BOT_TOKEN=тэг Телеграм-бота
```
Чтобы получить идентификатор приложения и его хэш, нужно пройти по адресу [https://my.telegram.org](https://my.telegram.org), залогиниться и создать приложение. В Device указать desktop (по крайней мере на данный момент).

Чтобы бот корректно реагировал на сообщения в группах, необходимо разрешить ему доступ к сообщениям. Это можно сделать командой /setprivacy через @BotFather.

Бот будет работать только при налии доступа к API, из которого он получает данные о пользователях и балансе.

В настоящий момент работает одна команда: `balance`, на которую бот отвечает сообщением с кнопкой "Проверить", при нажатии на котокую выводится всплывающее оповещение с балансом пользователя, который нажал на кнопку. 

При первом запуске приложения потребуется ввести код подтверждения логина. Запрос на ввод должен появиться в консоли.

Создать докер образ можно командой `docker build -f Dockerfile -t <имя образа> .`, если у вас консольный клиент. Запустить контейнер можно следующим образом:
```
docker run --name <название контейнера> -e 'TG_API_ID=<значение>' -e 'TG_API_HASH=<значение>' -e 'TG_BOT_TOKEN=<значение>' -it --net=host balance_bot:latest
```
Когда бот будет запущен и авторизован, можно отключиться от контейнера без его остановки, нажав Ctrl-P, затем Ctrl-Q.