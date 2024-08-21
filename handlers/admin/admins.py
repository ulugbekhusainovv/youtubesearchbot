from filters import IsAdmin,IsPrivate
from aiogram import types,html
from aiogram.filters import Command
from loader import dp,bot
from aiogram.types.reaction_type_emoji import ReactionTypeEmoji
from datetime import datetime, timedelta
import sqlite3
import random
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


DATABASE_FILE = "bot.db"

def db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    return conn

def create_channel_table():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY,
            username VARCHAR(30) NULL,
            name TEXT,
            telegram_id INTEGER,
            users_count VARCHAR(10) NULL,
            registration_date TEXT,
            invite_link TEXT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ensure the table is created at startup
create_channel_table()


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

class AddChannel(StatesGroup):
    waiting_for_channel_id = State()

@dp.message(Command('panel'), IsAdmin(), IsPrivate())
async def admin_panel(message: types.Message):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="📊Statistics",
            callback_data="statistics"
        ),
        InlineKeyboardButton(
            text="📢Kanallar ro'yxati",
            callback_data="list_channels"
        ),
        InlineKeyboardButton(
            text="❌",
            callback_data=f"deletemsg_{message.chat.id}"
        )
    )
    inline_keyboard.adjust(1)
    await message.answer("Assalamu alaykum admin panelga hush kelibsiz",reply_markup=inline_keyboard.as_markup())


@dp.callback_query(lambda query: query.data.startswith("back_panel"))
async def back_to_admin_panel(callback_query: types.CallbackQuery):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="📊Statistics",
            callback_data="statistics"
        ),
        InlineKeyboardButton(
            text="📢Kanallar ro'yxati",
            callback_data="list_channels"
        ),
        InlineKeyboardButton(
            text="❌",
            callback_data=f"deletemsg_{callback_query.message.chat.id}"
        )
    )
    inline_keyboard.adjust(1)
    await callback_query.message.edit_text("Assalamu alaykum admin panelga hush kelibsiz",reply_markup=inline_keyboard.as_markup())



@dp.callback_query(lambda query: query.data.startswith("deletemsg_"))
async def delmsg(callback_query: types.CallbackQuery):
    chat_id = int(callback_query.data.split('_')[-1])
    try:
        await bot.delete_message(chat_id=chat_id, message_id=callback_query.message.message_id)
    except:
        await callback_query.answer("Xatolik yuz berdi")


@dp.callback_query(lambda query: query.data.startswith("addchannel"))
async def add_channel_start(callback_query: types.CallbackQuery, state: FSMContext):
    bot_username = (await bot.me()).username    
    add_group_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Kanalga admin qilish", url=f"https://t.me/{bot_username}?startchannel=true")
            ],
            [
                InlineKeyboardButton(text="Guruhga admin qilish", url=f"https://t.me/{bot_username}?startgroup=true")
            ],
            [
                InlineKeyboardButton(text="⏪Orqaga", callback_data="back_panel")
            ]
            
        ]
    )
    await callback_query.message.edit_text("<b>Kanal yoki guruhni ulash uchun ID ni yoki Xabarni yuboring\nKanal ulashdan avval botni Admin  ekanligini tekshiring</b>", reply_markup=add_group_button)
    await state.set_state(AddChannel.waiting_for_channel_id)


@dp.message(AddChannel.waiting_for_channel_id,IsAdmin(), IsPrivate())
async def add_channel_id(message: types.Message, state: FSMContext):
    if message.forward_from_chat:
        channel_id = message.forward_from_chat.id
    else:
        channel_id = message.text
    try:
        channel = await bot.get_chat(chat_id=channel_id)
        channel_username = channel.username
        channel_name = channel.title
        channel_users_count = await bot.get_chat_member_count(chat_id=channel_id)
        invite_link = await bot.export_chat_invite_link(chat_id=channel_id)

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM channels WHERE telegram_id = ?', (channel_id,))
        if cursor.fetchone()[0] > 0:
            await message.answer(f"Bu {channel.type} allaqachon qo'shilgan. Boshqa kanal yoki guruh idsini tashlang")
            await state.set_state(AddChannel.waiting_for_channel_id)
            conn.close()
            await state.clear()
            return
        
        cursor.execute('''
            INSERT INTO channels (username, name, telegram_id, users_count, registration_date, invite_link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (channel_username, channel_name, channel_id, channel_users_count, datetime.now().strftime("%Y-%m-%d"), invite_link))
        conn.commit()
        conn.close()

        await state.clear()
        await message.answer(f"Juda soz {channel.type} muafaqiyatli ulandi!")
     
    except:
        bot_username = (await bot.me()).username
        # permissions = 'can_post_messages=true&can_edit_messages=true&can_delete_messages=true&can_invite_users=true&can_restrict_members=true&can_pin_messages=true&can_manage_topics=true'
        
        add_group_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Kanalga admin qilish", url=f"https://t.me/{bot_username}?startchannel=true")
                ],
                [
                    InlineKeyboardButton(text="Guruhga admin qilish", url=f"https://t.me/{bot_username}?startgroup=true")
                ]
            ]
        )
        
        await message.answer("Kanal topilmadi yoki unga kirish imkoni yo'q. Botni admin qilish uchun quyidagi tugmalardan birini tanlang:", reply_markup=add_group_button)
        await state.set_state(AddChannel.waiting_for_channel_id)


# @dp.message(Command('stat'))

@dp.callback_query(lambda query: query.data.startswith("statistics"))
async def statistic(callback_query: types.CallbackQuery):
    total_users = get_total_users()
    today_users = get_today_users()
    yesterday_users = get_yesterday_users()
    month_users = get_month_users()


    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="⏪Orqaga",
            callback_data="back_panel"
        ),
    )
    inline_keyboard.adjust(1)
    await callback_query.message.edit_text(
        f"📊 Bot Statistics\n\n"
        f"👤 Total members: {total_users}\n\n"
        f"📅 Members today: {today_users}\n"
        f"📅 Members yesterday: {yesterday_users}\n"
        f"📅 Members this month: {month_users}",
        reply_markup=inline_keyboard.as_markup()
        )

def get_channels():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()
    conn.close()
    return channels



@dp.callback_query(lambda query: query.data.startswith("list_channels"))
async def list_channels(callback_query: types.CallbackQuery):
    channels = get_channels()
    inline_keyboard = InlineKeyboardBuilder()
    for channel in channels:
        channel_id = channel[3]
        channel_name = channel[2]
        inline_keyboard.add(
            InlineKeyboardButton(
                text=str(channel_name),
                callback_data=f"settings_{channel_id}"
            )
        )
    inline_keyboard.add(
        InlineKeyboardButton(
            text="➕Kanal qo'shish",
            callback_data="addchannel"
        ),
        InlineKeyboardButton(
            text="⏪Orqaga",
            callback_data="back_panel"
        ),
    )
    inline_keyboard.adjust(1)
    await callback_query.message.edit_text("Kanallar ro'yxati:", reply_markup=inline_keyboard.as_markup())

@dp.callback_query(lambda query: query.data.startswith("settings_"))
async def channel_settings_callback_handler(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split('_')[-1])
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="♻️Yangi link (invite link)",
            callback_data=f"new_invite_{channel_id}"
        ),
        InlineKeyboardButton(
            text="🗑️Kanalni o'chirish",
            callback_data=f"delete_{channel_id}"
        ),
        InlineKeyboardButton(
            text="⏪Orqaga",
            callback_data="list_channels"
        )
    )
    inline_keyboard.adjust(1)
    await callback_query.message.edit_text(f"Kanal sozlamalari: {channel_id}", reply_markup=inline_keyboard.as_markup())

@dp.callback_query(lambda query: query.data.startswith("new_invite_"))
async def new_invite_link_callback_handler(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split('_')[-1])
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="⏪ orqaga",
            callback_data=f"settings_{channel_id}"
        )
    )
    try:
        invite_link = await bot.create_chat_invite_link(chat_id=channel_id)
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE channels SET invite_link = ? WHERE telegram_id = ?", (invite_link.invite_link, channel_id))
        conn.commit()
        conn.close()

        await callback_query.message.edit_text(f"Yangi invite link: {html.link(value='link', link=invite_link.invite_link)}",disable_web_page_preview=True,reply_markup=inline_keyboard.as_markup())
    except Exception as e:
        await callback_query.message.edit_text(f"Link yaratishda xato: {e}\nBot ruxsatlarini tekshiring", reply_markup=inline_keyboard.as_markup())


@dp.callback_query(lambda query: query.data.startswith("delete_"))
async def delete_channel_callback_handler(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split('_')[-1])
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM channels WHERE telegram_id = ?", (channel_id,))
        conn.commit()
        conn.close()
        try:
            await bot.leave_chat(chat_id=channel_id)
        except:
            pass
        await callback_query.message.edit_text(f"Kanal o'chirildi: {channel_id}\nVa bot chatni tark etdi")
    except Exception as e:
        await callback_query.message.edit_text(f"Kanalni o'chirishda xato: {e}")



@dp.message(Command('panel'), ~IsAdmin(), IsPrivate())
async def not_admin_statistic(message: types.Message):
    reaction_list = ["😁", "🤔","🤣","🤪", "🗿", "🆒","😎", "👾", "🤷‍♂", "🤷"]
    try:
        await bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=random.choice(reaction_list))],
            is_big=False
        )
    except:
        pass
    await message.reply("Siz admin emassiz!", disable_notification=True, protect_content=True)

