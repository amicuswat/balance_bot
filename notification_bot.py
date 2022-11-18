import os
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv

balance_cache = 0
last_notification_cache = None

API_URL = 'http://localhost:8000/api/v1/'


async def call_api(endpoint):
    full_url = urljoin(API_URL, endpoint)
    response = requests.get(full_url)
    response.raise_for_status()
    return response.json()


async def call_api_post(endpoint, params):
    full_url = urljoin(API_URL, endpoint)
    print(full_url)
    response = requests.post(full_url, data=params)
    response.raise_for_status()
    return response.json()


async def is_permited_chat(chat_id):
    chats = await call_api('groups')
    print(chat_id)

    allowed_chat_ids = [chat['telegram_id'] for chat in chats]
    print(allowed_chat_ids)

    return chat_id in allowed_chat_ids


async def get_chats_to_notify_ids():
    chats = await call_api('groups')
    chats_to_notify_ids = [chat['telegram_id']
                           for chat in chats if chat['is_notification_list']]

    return chats_to_notify_ids


async def should_notify(balance):
    global last_notification_cache
    bot_settings = await call_api('bots/1')
    if balance > bot_settings['first_limit']:
        return

    if not last_notification_cache:
        last_notification_cache = datetime.now()
        return True

    if datetime.now() - last_notification_cache > timedelta(hours=bot_settings['first_limit_delay']):
        last_notification_cache = datetime.now()
        return True

    if (balance < bot_settings['critical_limit']
        and datetime.now() - last_notification_cache > timedelta(hours=bot_settings['critical_limit_delay'])):
        last_notification_cache = datetime.now()
        return True


@events.register(events.NewMessage(incoming=True, pattern='Баланс Фригат Прокси'))
async def check_balance_handler(event):
    current_chat = await event.get_chat()

    balance = balance_cache

    if not await is_permited_chat(current_chat.id):
        await event.reply(f'У вас нет доступа к этой информации')
        return

    await event.respond(f'Баланс ЛК Фригат составляет: {balance} руб.')


@events.register(events.NewMessage(incoming=True, pattern='/start'))
async def start_handler(event):
    await event.respond('Меню:', buttons=[
        Button.text('Баланс Фригат Прокси', resize=True, single_use=False)
    ])


async def broadcast(bot, balance):
    print('Will send notification')
    chats_to_notify_ids = await get_chats_to_notify_ids()
    print(chats_to_notify_ids)

    if not chats_to_notify_ids:
        return

    for chat_id in chats_to_notify_ids:
        try:
            await bot.send_message(chat_id, f'Необходимо срочно пополнить баланс! На текущий момент осталось: {balance} руб')
        except ValueError:
            print('Chat ID not found.')

    # todo ToMany messages tg limit Exception

    # todo Exception if chat is closed


async def frigate_connector(bot, frigate_api_key, frigate_api_url):
    global last_notification_cache, balance_cache

    params = {
        'api_key': frigate_api_key
    }

    while True:
        bot_settings = await call_api('bots/1')
        print(bot_settings)

        delay = bot_settings['api_requests_interval']

        try:
            response = requests.get(frigate_api_url, params=params)
        except ConnectionError as ex:
            print(ex)
            await asyncio.sleep(delay)
            continue

        except Exception as ex:
            print(type(ex))
            await asyncio.sleep(delay)
            continue

        response.raise_for_status()

        balance = int(response.json()['balance'])
        balance_params = {
            "amount": f'{balance}'
        }

        await call_api_post('balancelist/', balance_params)

        balance_cache = balance

        if await should_notify(balance):
            await broadcast(bot, balance)

        await asyncio.sleep(delay)


if __name__ == '__main__':
    load_dotenv()

    frigate_api_key = os.environ['FRIGAT_API_KEY']
    frigate_api_url = 'https://frigate-proxy.ru/ru/api/balance'

    bot = TelegramClient('test_session', api_id=os.environ['TG_API_ID'], api_hash=os.environ['TG_API_HASH'])
    bot.start(bot_token=os.environ['TG_BOT_TOKEN'])

    with bot:
        bot.add_event_handler(start_handler)
        bot.add_event_handler(check_balance_handler)
        bot.loop.create_task(frigate_connector(bot, frigate_api_key, frigate_api_url))
        bot.run_until_disconnected()
