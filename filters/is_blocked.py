from aiogram.filters import Filter
from aiogram import types
import sqlite3


DATABASE_FILE = "bot.db"

def db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    return conn


def is_user_blocked(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM blocked_users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None



class IsBlocked(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return is_user_blocked(message.from_user.id)
