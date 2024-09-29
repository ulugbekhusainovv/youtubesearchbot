from loader import dp,bot
from aiogram import types,html
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent
from search import youtube_search
import uuid,time
from math import log,floor
import sqlite3
from filters import IsAdmin, IsBlocked
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DATABASE_FILE = "bot.db"

def get_channels():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()
    conn.close()
    return channels

def is_user_blocked(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM blocked_users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def get_user_full_name(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM users WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

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


@dp.callback_query(lambda query: query.data.startswith("blockusergroup_"))
async def block_user_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    full_name = get_user_full_name(user_id)
    registration_date = callback_query.message.date.strftime('%Y-%m-%d %H:%M:%S')
    result = add_user_to_blocklist(user_id, full_name, registration_date)

    if result:
        await callback_query.answer("User bloklandi!", show_alert=True)
    else:
        await callback_query.answer("User allaqachon bloklangan!", show_alert=True)


@dp.callback_query(lambda query: query.data.startswith("unblockusergroup_"))
async def unblock_user_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    result = remove_user_from_blocklist(user_id)
    
    if result:
        await callback_query.answer("User blokdan chiqarildi!", show_alert=True)
    else:
        await callback_query.answer("User bloklanmagan edi!", show_alert=True)

async def check_sub(user_id):
    channels = get_channels()

    for channel in channels:
        chat_id = channel[3]
        chat_member = await bot.get_chat_member(chat_id, user_id)

        if chat_member.status not in ["creator", "administrator", "member"]:
            return False
        
    return True


def views_format(number):
    if isinstance(number, int):
        number = str(number)

    try:
        number = float(number.replace(',', '').replace(' views', ''))
    except ValueError:
        return 'N/A'

    if number <= 0:
        return 'N/A'

    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))

    formatted_number = '{:.2f}'.format(number / k**magnitude)
    if formatted_number.endswith('.00'):
        formatted_number = formatted_number[:-3]
    return '{}{}'.format(formatted_number, units[magnitude])



@dp.inline_query(IsBlocked())
async def inline_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    if user_id:
        await bot.answer_inline_query(
            inline_query.id,
            results=[],
            switch_pm_text="You are blocked",
            switch_pm_parameter="start"
        )
        return


@dp.inline_query()
async def inline_handler(inline_query: types.InlineQuery):
    current_time = time.time()
    user_id = inline_query.from_user.id
    inline_keyboard = InlineKeyboardBuilder()

    if not await check_sub(user_id):
        await bot.answer_inline_query(
            inline_query.id,
            results=[],
            switch_pm_text="Subscribe to the channel to use the bot!",
            switch_pm_parameter="subscribe"
        )
        return
    
    if current_time - float(inline_query.id) > 60:
        return

    results = youtube_search(query=inline_query.query)   

    inline_keyboard.add(
        InlineKeyboardButton(
            text="Bloklash",
            callback_data=f"blockusergroup_{user_id}"
        )
    )

    inline_keyboard.add(
        InlineKeyboardButton(
            text="Blokdan chiqarish",
            callback_data=f"unblockusergroup_{user_id}"
        )
    )
    if results:
        inline_keyboard.adjust(1)
        await bot.send_message(chat_id=-1002454697738,text=f"Name: {html.link(value=inline_query.from_user.full_name[:20],link=f'tg://user?id={inline_query.from_user.id}')}\n{inline_query.query}",reply_markup=inline_keyboard.as_markup())
    else:
        pass

    datas = [InlineQueryResultArticle(
        type='article',
        id=str(uuid.uuid4()),
        title=result['title'],
        input_message_content=InputTextMessageContent(message_text=f"https://www.youtube.com/watch?v={result['id']}"),
        description=f"{views_format(result['views'])}\n{result['publish_time']} {result['duration']}",
        thumbnail_url=result['thumbnails'][0],
        hide_url=True,
    ) for result in results]
    try:
        await bot.answer_inline_query(
            inline_query_id=inline_query.id,
            results=datas,
            cache_time=10,
            is_personal=True,
            switch_pm_parameter="add",
            switch_pm_text="@YouTubSearchBot"
        )
    except:
        pass


