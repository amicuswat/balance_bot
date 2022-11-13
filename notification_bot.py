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
    allowed_chat_ids = [chat['telegram_id'] for chat in chats]

    return chat_id in allowed_chat_ids


async def get_chats_to_notify_ids():
    chats = await call_api('groups')
    chats_to_notify_ids = [chat['telegram_id'] for chat in chats if chat['is_notification_list']]

    return chats_to_notify_ids


async def should_notify(balance):
    global last_notification_cache
    bot_settings = await call_api('bots/1')
    if balance > bot_settings['first_limit']:
        print('balance is bigger do nothing')
        return
    print('balance is less continue')

    if not last_notification_cache:
        print('notify first time, save time')
        last_notification_cache = datetime.now()
        return True
    print('Is it time to notify again?')

    if datetime.now() - last_notification_cache > timedelta(hours=bot_settings['first_limit_delay']):
        print('time to notify again')
        last_notification_cache = datetime.now()
        return True
    print('not notify is it critical')

    if (balance < bot_settings['critical_limit']
        and datetime.now() - last_notification_cache > timedelta(hours=bot_settings['critical_limit_delay'])):
        print('critical balance notify')
        last_notification_cache = datetime.now()
        return True


@events.register(events.NewMessage(incoming=True, pattern='Прoвeрить'))
async def check_balance_handler(event):
    current_chat = await event.get_chat()

    balance = balance_cache

    if not await is_permited_chat(current_chat.id):
        print(current_chat)
        await event.reply(f'У вас нет доступа к этой информации')
        return
    await event.reply(f'Ваш баланс: {balance}')
    #await event.delete()


@events.register(events.NewMessage(incoming=True, pattern='/balance'))
async def start_handler(event):
    await event.reply('Нажмите "Проверить", чтобы узнать ваш баланс.', buttons=[
        Button.text('Прoвeрить', resize=True, single_use=False)
    ])


async def broadcast(bot, balance):
    print('Will send notification')
    chats_to_notify_ids = await get_chats_to_notify_ids()
    print(chats_to_notify_ids)

    if not chats_to_notify_ids:
        return

    for chat_id in chats_to_notify_ids:
        try:
            await bot.send_message(chat_id, f'Пополните баланс, осталось всего: {balance}')
        except ValueError:
            print('Chat ID not found.')

    # todo ToMany messages tg limit Exception

    # todo Exception if chat is closed


async def frigate_connector(bot, delay, frigate_api_key, frigate_api_url):
    global last_notification_cache, balance_cache

    print('Start looping')
    params = {
        'api_key': frigate_api_key
    }
    # bot_id = 1
    # last_notification = datetime.now()
    while True:
        print(1)
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
        print(response.json())


        balance = response.json()['balance']

        balance_params = {
            "amount": f'{balance}'
        }

        await call_api_post('balancelist/', balance_params)
        # todo Delete after test
        balance = 1500

        balance_cache = balance
        print(2)
        if await should_notify(balance):
            await broadcast(bot, balance)
        print(3)

        await asyncio.sleep(delay)
        print(4)


if __name__ == '__main__':
    load_dotenv()
    delay = 60 # seconds
    frigate_api_key = os.environ['FRIGAT_API_KEY']
    frigate_api_url = 'https://frigate-proxy.ru/ru/api/balance'

    bot = TelegramClient('test_session', api_id=os.environ['TG_API_ID'], api_hash=os.environ['TG_API_HASH'])
    bot.start(bot_token=os.environ['TG_BOT_TOKEN'])

    with bot:
        bot.add_event_handler(start_handler)
        bot.add_event_handler(check_balance_handler)
        bot.loop.create_task(frigate_connector(bot, delay, frigate_api_key, frigate_api_url))
        bot.run_until_disconnected()
