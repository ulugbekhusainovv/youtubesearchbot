from loader import dp,bot
from aiogram import types,html
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent
from search import youtube_search
import uuid,time
from math import log,floor
import sqlite3



def get_channels():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()
    conn.close()
    return channels

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



@dp.inline_query()
async def inline_handler(inline_query: types.InlineQuery):
    current_time = time.time()
    user_id = inline_query.from_user.id

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
