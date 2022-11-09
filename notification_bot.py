import os
import asyncio
from urllib.parse import urljoin

import requests
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv


API_URL = 'http://localhost:8000/api/v1/'


async def call_api(endpoint):
    full_url = urljoin(API_URL, endpoint)
    response = requests.get(full_url)
    response.raise_for_status()
    return response.json()


@events.register(events.CallbackQuery(data=b'check'))
async def check_balance_handler(event):
    current_user = await event.get_sender()
    # users = await call_api('members')
    # organisation = [user['organisation'] for user in users if user['telegram_id'] == current_user.id][0]
    # balances = await call_api('balancelist')
    # balance = [balance['amount'] for balance in balances if balance['organisation'] == organisation][0]
    await event.answer(f'Ваш баланс: {balance}', alert=True)


@events.register(events.NewMessage(incoming=True, pattern='balance'))
async def start_handler(event):
    # chat = await event.get_chat()
    # allowed_chats = await call_api('organisations')
    await event.reply('Нажмите "проверить", чтобы узнать ваш баланс.', buttons=[
        Button.inline('Проверить', b'check')
    ])
    # if chat.id in [chat['chat_id'] for chat in allowed_chats]:



async def broadcast(bot, balance):
    print('Started')
    users = await call_api('members')

    if users:
        for user in users:
            try:
                await bot.send_message(user['telegram_id'], f'Ваш баланс: {balance}')
            except ValueError:
                print('User ID not found.')


async def frigate_connector(bot, delay, frigate_api_key, frigate_api_url):
    print('Start looping')
    params = {
        'api_key': frigate_api_key
    }
    # bot_id = 1
    # last_notification = datetime.now()

    while True:

        await asyncio.sleep(delay)
        response = requests.get(frigate_api_url, params=params)
        response.raise_for_status()

        balance = response.json()['balance']
        print(balance)
        print(type(balance))

        # test values
        balance = 1000
        # test values end

        if balance < 2000:
            broadcast(bot, balance)

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
    delay = 30
    frigate_api_key = os.environ['FRIGAT_API_KEY']
    frigate_api_url = 'https://frigate-proxy.ru/ru/api/balance'

    bot = TelegramClient('test_session', api_id=os.environ['TG_API_ID'], api_hash=os.environ['TG_API_HASH'])
    bot.start(bot_token=os.environ['TG_BOT_TOKEN'])

    with bot:
        bot.add_event_handler(start_handler)
        bot.add_event_handler(check_balance_handler)
        bot.loop.create_task(frigate_connector(bot, delay, frigate_api_key, frigate_api_url))
        bot.run_until_disconnected()
