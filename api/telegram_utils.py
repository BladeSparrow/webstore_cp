from telegram import Bot
from telegram.error import TelegramError
from tokens import BOT_TOKEN_hide as BOT_TOKEN



async def send_telegram_message_async(chat_id, message):

    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")
        return False

from asgiref.sync import async_to_sync


def send_telegram_message(chat_id, message):

    try:
        async_to_sync(send_telegram_message_async)(chat_id, message)
        return True
    except Exception as e:
        print(f"Error in send_telegram_message wrapper: {e}")
        return False

