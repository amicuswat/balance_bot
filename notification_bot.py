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


async def is_permited_user(user_id):
    users = await call_api('members')
    allowered_users_ids = [user['telegram_id'] for user in users if user['is_bot_user']]

    return user_id in allowered_users_ids


async def get_users_to_notify_ids():
    users = await call_api('members')
    users_to_notify_ids = [user['telegram_id'] for user in users if user['is_notification_list']]

    return users_to_notify_ids


async def should_notify(balance):
    bot_settings = await call_api('bots/1')
    if balance > bot_settings['first_limit']:
        print('balance is bigger do nothing')
        return
    print('balance is less continue')

    if not last_notification_cache:
        print('notify first time, save time')
        last_notification_cache = datetime.now()
        return True

    if datetime.now() - last_notification_cache > timedelta(hours=bot_settings['first_limit_delay']):
        print('time to notify again')
        last_notification_cache = datetime.now()
        return True

    if balance < bot_settings['critical_limit']
        and datetime.now() - last_notification_cache > timedelta(hours=bot_settings['critical_limit_delay']):
        print('criticl balance notify')
        last_notification_cache = datetime.now()
        return True


@events.register(events.CallbackQuery(data=b'check'))
async def check_balance_handler(event):
    current_user = await event.get_sender()

    balance = balance_cache

    if not await is_permited_user(current_user.id):
        await event.answer(f'У вас нет доступа к этой информации', alert=True)
        return

    await event.answer(f'Ваш баланс: {balance}', alert=True)


@events.register(events.NewMessage(incoming=True, pattern='/balance'))
async def start_handler(event):
    await event.reply('Нажмите "проверить", чтобы узнать ваш баланс.', buttons=[
        Button.inline('Проверить', b'check')
    ])


async def broadcast(bot, balance):
    print('Will send notification')
    users_to_notify_ids = get_users_to_notify_ids()

    if not users_to_notify_ids:
        return

    for user_id in users_to_notify_ids:
        try:
            await bot.send_message(user_id, f'Ваш баланс: {balance}')
        except ValueError:
            print('User ID not found.')

    # todo ToMany messages tg limit Exception

    # todo Exception if chat is closed


async def frigate_connector(bot, delay, frigate_api_key, frigate_api_url):
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
            await asyncio.sleep(delay)
            continue

        except Exception as ex:
            print(type(ex))
            await asyncio.sleep(delay)
            continue

        response.raise_for_status()
        print(response.json())


        balance = response.json()['balance']
        # todo Delete after test
        balance = 10000
        # todo Save to DB
        balance_cache = balance
        print(2)
        if await should_notify(balance):
            await broadcast(bot, balance)
        print(3)

        await asyncio.sleep(delay)
        print(4)

        # bot_settings = get_bot_settings(bot_id)
        # if balance < bot_settings['critical_limit']['limit']:
        #     should_send_message = ((datetime.now() - last_notification)
        #                            > timedelta(hours=bot_settings['critical_limit']['delay']))
        #     if should_send_message:
        #         broadcast(bot, balance)
        #         last_notification = datetime.now()
        #         continue



if __name__ == '__main__':
    load_dotenv()
    delay = 5
    balance_cache = 0
    last_notification_cache = datetime.now()
    frigate_api_key = os.environ['FRIGAT_API_KEY']
    frigate_api_url = 'https://frigate-proxy.ru/ru/api/balance'

    bot = TelegramClient('test_session', api_id=os.environ['TG_API_ID'], api_hash=os.environ['TG_API_HASH'])
    bot.start(bot_token=os.environ['TG_BOT_TOKEN'])

    with bot:
        bot.add_event_handler(start_handler)
        bot.add_event_handler(check_balance_handler)
        bot.loop.create_task(frigate_connector(bot, delay, frigate_api_key, frigate_api_url))
        bot.run_until_disconnected()
