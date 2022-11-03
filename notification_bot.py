import os
import asyncio
from time import sleep

from telethon import TelegramClient, events, Button
from dotenv import load_dotenv


USERS = []


@events.register(events.CallbackQuery(data=b'check'))
async def check_balance_handler(event):
    # Pop-up message with alert
    balance = ''
    await event.answer(f'Ваш баланс: {balance}', alert=True)


@events.register(events.NewMessage(incoming=True, pattern='balance'))
async def start_handler(event):
    user = await event.get_sender()
    if user not in USERS:
        USERS.append(user)
    await event.reply('Нажмите "проверить, чтобы узнать ваш баланс."', buttons=[
        Button.inline('Проверить', b'check')
    ])


async def broadcast(bot, delay):
    print('Started')
    while True:
        await asyncio.sleep(delay)
        if USERS:
            for user_id in USERS:
                await bot.send_message(user_id, f'Ваш баланс: {0}')


if __name__ == '__main__':
    load_dotenv()

    bot = TelegramClient('test_session', api_id=os.environ['TG_API_ID'], api_hash=os.environ['TG_API_HASH'])
    bot.start(bot_token=os.environ['TG_BOT_TOKEN'])

    with bot:
        bot.add_event_handler(start_handler)
        bot.add_event_handler(check_balance_handler)
        bot.loop.create_task(broadcast(bot, delay=15))
        bot.run_until_disconnected()
