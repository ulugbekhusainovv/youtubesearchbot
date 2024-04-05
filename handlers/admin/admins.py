# from filters import IsAdmin,IsPrivate
from aiogram import types
from aiogram.filters import Command
from loader import dp,bot
from aiogram.types.reaction_type_emoji import ReactionTypeEmoji
from datetime import datetime, timedelta
import sqlite3
import random


DATABASE_FILE = "bot.db"


def get_total_users():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    return total_users

def get_today_users():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE registration_date >= '{today}'")
    today_users = cursor.fetchone()[0]
    conn.close()
    return today_users

def get_yesterday_users():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE registration_date >= '{yesterday}' AND registration_date < '{datetime.now().strftime('%Y-%m-%d')}'")
    yesterday_users = cursor.fetchone()[0]
    conn.close()
    return yesterday_users

def get_month_users():
    first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE registration_date >= '{first_day_of_month}'")
    month_users = cursor.fetchone()[0]
    conn.close()
    return month_users

@dp.message(Command('stat'))
async def statistic(message: types.Message):
    total_users = get_total_users()
    today_users = get_today_users()
    yesterday_users = get_yesterday_users()
    month_users = get_month_users()

    await message.reply(
        f"📊 Bot Statistics\n\n"
        f"👤 Total members: {total_users}\n\n"
        f"📅 Members today: {today_users}\n"
        f"📅 Members yesterday: {yesterday_users}\n"
        f"📅 Members this month: {month_users}"
    )

# @dp.message(Command('panel') ,IsAdmin(), IsPrivate())
# async def admin_panel(message: types.Message):
#     await message.answer("Salom")


# @dp.message(Command('panel'), ~IsAdmin(), IsPrivate())
# async def not_admin_statistic(message: types.Message):
#     reaction_list = ["😁", "🤔","🤣","🤪", "🗿", "🆒","😎", "👾", "🤷‍♂", "🤷"]
#     try:
#         await bot.set_message_reaction(
#             chat_id=message.chat.id,
#             message_id=message.message_id,
#             reaction=[ReactionTypeEmoji(emoji=random.choice(reaction_list))],
#             is_big=False
#         )
#     except:
#         pass
#     await message.reply("Siz admin emassiz!", disable_notification=True, protect_content=True)

