from loader import bot,dp
from aiogram import types
from typing import Union
import sqlite3
from aiogram.types import  InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_channels():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()
    conn.close()
    return channels

def is_user_blocked(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM blocked_users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None



async def check_sub(user_id):
    channels = get_channels()

    for channel in channels:
        chat_id = channel[3]
        chat_member = await bot.get_chat_member(chat_id, user_id)

        if chat_member.status not in ["creator", "administrator", "member"]:
            return False
        
    return True



@dp.callback_query(lambda query: query.data.startswith("check_subscriptions"))
async def check_subscription(callback_query: types.CallbackQuery):
    is_subscribed = await check_sub(callback_query.from_user.id)
    if is_subscribed:
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Keep it up!")
        await bot.delete_message(callback_query.message.chat.id, message_id=callback_query.message.message_id)
    else:
        await callback_query.answer("Please subscribe to our channels below, then you can use the bot", show_alert=True)


async def joinchat(user_id):
    channels = get_channels()
    inline_keyboard = InlineKeyboardBuilder()
    uns = False
    for channel in channels:
        chat_id, chat_username, invite_link = channel[3], channel[1], channel[-1]
        chat_member = await bot.get_chat_member(chat_id, user_id)

        if chat_member.status not in ["creator", "administrator", "member"]:
            if chat_username:
                chat_url = f"https://t.me/{chat_username}"
            else:
                chat_url = invite_link

            button = InlineKeyboardButton(text=f"➕ Subscribe", url=chat_url)
            uns = True
            inline_keyboard.add(button)

    check_button = InlineKeyboardButton(text="✅ Confirm", callback_data="check_subscriptions")
    inline_keyboard.add(check_button)
    inline_keyboard.adjust(1)

    if uns:
        await bot.send_message(user_id, "Please subscribe to our channels below, then you can use the bot.", parse_mode='html', reply_markup=inline_keyboard.as_markup())
        return False
    else:
        return True
    



async def blocked_user(user_id):
    uns = False
    if is_user_blocked(user_id):
        uns = True
    if uns:
        await bot.send_message(user_id, "You have been blocked by admins. To be unblocked, please contact our support.", parse_mode='html')
        return False
    else:
        return True
    

