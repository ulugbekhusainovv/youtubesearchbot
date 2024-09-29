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
from keyboards.inline.buttons import blocked_users_list_button, BlockedUsersListPaginatorCallback,page_size

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

create_channel_table()

def create_blocked_users_table():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_users (
            id INTEGER PRIMARY KEY,
            fullname TEXT NULL,
            user_id INTEGER,
            registration_date TEXT
        )
    ''')
    conn.commit()
    conn.close()


create_blocked_users_table()

def get_blocked_user(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM blocked_users WHERE user_id = ?
    ''', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_full_name(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM users WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None
# User bloklanganmi yoki yo'qmi tekshirish
def is_user_blocked(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM blocked_users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def is_valid_user(user_id):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        print(f"Xatolik: {e}")
        return False
    finally:
        connection.close()
# Barcha bloklangan userlarni olish
def get_blocked_users():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocked_users")
    blocked_users = cursor.fetchall()
    conn.close()
    return blocked_users


def add_user_to_blocklist(user_id, full_name, registration_date):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    if not is_user_blocked(user_id):
        cursor.execute("INSERT INTO blocked_users (fullname, user_id, registration_date) VALUES (?,?,?)", (full_name,user_id,registration_date,))
        conn.commit()
        return True
    return False


def remove_user_from_blocklist(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Userni bloklanganlar ro'yxatida borligini tekshirish
    if is_user_blocked(user_id):
        # Agar user bloklangan bo'lsa, uni o'chirish
        cursor.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    return False



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

class BlockUserState(StatesGroup):
    waiting_for_user_id = State()


class UnBlockUserState(StatesGroup):
    waiting_for_user_id = State()


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
            text="🦵Bloklanganlar",
            callback_data="blocked_users"
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
            text="🦵Bloklanganlar",
            callback_data="blocked_users"
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




@dp.callback_query(lambda query: query.data.startswith("blocked_users"))
async def blocked_users(callback_query: types.CallbackQuery):
    inline_keyboard = InlineKeyboardBuilder()
    try:
        callback_data_parts = callback_query.data.split('_')
        if len(callback_data_parts) > 2 and callback_data_parts[-1].isdigit():
            page = int(callback_data_parts[-1])
        else:
            page = 0

        blocked_users = get_blocked_users()
        if blocked_users:
            await callback_query.message.edit_text(
                text="Bloklanganlar ro'yxati",
                reply_markup=blocked_users_list_button(page=page)
            )
        else:
            inline_keyboard.add(
                InlineKeyboardButton(
                    text="Qo'shish",
                    callback_data="add_block_user"
                )
            )
            inline_keyboard.add(
                InlineKeyboardButton(
                    text="⏪ Orqaga",
                    callback_data="back_panel"
                )
            )
            inline_keyboard.adjust(1)
            await callback_query.message.edit_text(
                text="Bloklangan foydalanuvchilar topilmadi.",
                reply_markup=inline_keyboard.as_markup()
            )

    except Exception as error:
        await callback_query.answer(f"Xatolik: {error}", show_alert=True)


@dp.callback_query(BlockedUsersListPaginatorCallback.filter())
async def blocked_user_paginator_edit(callback_query: types.CallbackQuery, callback_data: BlockedUsersListPaginatorCallback):
    page = int(callback_data.page)
    action = callback_data.action
    length = int(callback_data.length)
    if action == 'next':
        if (page+1)*page_size >=length:
            page = page
        else:
            page += 1
    else:
        if page > 0:
            page = page - 1
        else:
            page=page
    await callback_query.message.edit_text(text=f"Bloklanganlar ro'yxati", reply_markup=blocked_users_list_button(page=page))


@dp.callback_query(lambda query: query.data.startswith("add_block_user"))
async def add_block_user(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Bloklanishi kerak bo'lgan user ID sini kiriting:")

    await state.set_state(BlockUserState.waiting_for_user_id)

# Xabarni qayta ishlash va user_id ni olish
@dp.message(BlockUserState.waiting_for_user_id)
async def process_block_user_id(message: types.Message, state: FSMContext):
    user_id = message.text.strip()
    inline_keyboard = InlineKeyboardBuilder()

    if not user_id.isdigit():
        await message.answer("Iltimos, to'g'ri ID kiriting.")
        return
    
    full_name = get_user_full_name(user_id)
    registration_date = message.date.strftime('%Y-%m-%d %H:%M:%S')
    result = add_user_to_blocklist(user_id, full_name, registration_date)

    inline_keyboard.add(
        InlineKeyboardButton(
            text="Qo'shish",
            callback_data="add_block_user"
        )
    )
    if result:
        await message.answer(f"User {user_id} bloklandi!",reply_markup=inline_keyboard.as_markup())
    else:
        await message.answer(f"User {user_id} allaqachon bloklangan!",reply_markup=inline_keyboard.as_markup())
    
    await state.clear()


@dp.callback_query(lambda query: query.data.startswith("rm_block_user"))
async def rm_block_user(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Blokdan chiqishi kerak bo'lgan user ID sini kiriting:")

    await state.set_state(UnBlockUserState.waiting_for_user_id)



@dp.message(UnBlockUserState.waiting_for_user_id)
async def process_unblock_user(message: types.Message, state: FSMContext):
    user_id = message.text.strip()
    if not user_id.isdigit():
        await message.answer("Iltimos, to'g'ri ID kiriting.")
        return
    
    result = remove_user_from_blocklist(user_id)
    
    if result:
        await message.answer("User blokdan chiqarildi!")
    else:
        await message.answer("User bloklanmagan edi!")

    await state.clear()




@dp.callback_query(lambda query: query.data.startswith("block_user_"))
async def block_user_data(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split('_')
    block_user_id = int(data_parts[-1])
    page = int(data_parts[-2]) if len(data_parts) > 2 else 0
    inline_keyboard = InlineKeyboardBuilder()
    blocked_user = get_blocked_user(block_user_id)

    try:
        if blocked_user:
            if is_valid_user(blocked_user[2]):
                inline_keyboard.add(
                    InlineKeyboardButton(
                        text=f"Id: {blocked_user[2]}",
                        url=f"tg://user?id={blocked_user[2]}"
                    )
                )
            else:
                inline_keyboard.add(
                    InlineKeyboardButton(
                        text="Foydalanuvchi topilmadi",
                        callback_data="no_user_found"
                    )
                )
        else:
            inline_keyboard.add(
                InlineKeyboardButton(
                    text="Foydalanuvchi topilmadi",
                    callback_data="no_user_found"
                )
            )
        inline_keyboard.add(
            InlineKeyboardButton(
                text="Blokdan chiqarish",
                callback_data=f"unblock_user_{page}_{block_user_id}"
            )
        )

        inline_keyboard.add(
            InlineKeyboardButton(
                text="⏪ orqaga",
                callback_data=f"blocked_users_{page}"
            )
        )
        inline_keyboard.adjust(1)


        if blocked_user:
            await callback_query.message.edit_text(f"User ma'lumoti: {blocked_user[1]},\nUser ID: {html.code(value=blocked_user[2])},\nRegistration Date: {blocked_user[3]}",reply_markup=inline_keyboard.as_markup())
        else:
            await callback_query.message.edit_text(
                "Foydalanuvchi topilmadi.",
            )

    except Exception as error:
        await callback_query.message.edit_text(f"Xatolik: {error}", reply_markup=inline_keyboard.as_markup())


@dp.callback_query(lambda query: query.data.startswith("unblock_user_"))
async def unblock_user_clq(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split('_')
    user_id = int(data_parts[-1])
    page = int(data_parts[-2]) if len(data_parts) > 2 else 0
    result = remove_user_from_blocklist(user_id)
    if result:
        await callback_query.answer("User blokdan chiqarildi!",show_alert=True)
        await callback_query.message.edit_text(text="Bloklanganlar ro'yxati", reply_markup=blocked_users_list_button(page=page))

    else:
        await callback_query.answer("User bloklanmagan edi!",show_alert=True)