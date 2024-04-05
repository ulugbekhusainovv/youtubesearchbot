from loader import dp,bot
from aiogram import types,html,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
from datetime import datetime
from aiogram.types import  InlineKeyboardButton,InlineKeyboardMarkup
conn = sqlite3.connect('bot.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(30) NULL,
        full_name TEXT,
        telegram_id INTEGER,
        registration_date TEXT
    )
''')
conn.commit()

async def is_user_registered(telegram_id):
    cursor.execute('''
        SELECT telegram_id FROM users WHERE telegram_id=?
    ''', (telegram_id,))
    result = cursor.fetchone()
    return result is not None

def start_button():
    btn = InlineKeyboardBuilder()
    
    btn.button(text="Search in Bot", switch_inline_query_current_chat='')
    btn.button(text=f"Search in Chat",switch_inline_query='')
    btn.adjust(1)
    return btn.as_markup()


@dp.message(F.text)
async def start_bot(message:types.Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    is_premium = message.from_user.is_premium
    username = message.from_user.username

    if not await is_user_registered(telegram_id):
        registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO users (username,full_name,telegram_id,registration_date)
            VALUES (?, ?, ?, ?)
        ''', (username,full_name, telegram_id, registration_date))
        conn.commit()
        await bot.send_message(chat_id=-1002104559125,text=f"New 👤: {full_name}\nUsername📩: {html.code(value=username)}\nTelegram 🆔: {html.code(value=telegram_id)}\nReg 📆: {registration_date}\nPremium🤑: {is_premium}",reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Profile", url=f"tg://user?id={telegram_id}")
            ]
        ]
))
    await message.answer(f"Hello {message.from_user.full_name} this bot is a YouTube search tool, choose one of the following buttons to search", reply_markup=start_button())


