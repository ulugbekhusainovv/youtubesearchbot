from loader import dp,bot
from aiogram import types,html
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent
from search import youtube_search
import uuid,time
from math import log,floor

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

    if current_time - float(inline_query.id) > 60:
        return

    results = youtube_search(query=inline_query.query)    
    datas = [InlineQueryResultArticle(
        type='article',
        id=str(uuid.uuid4()),
        title=result['title'],
        input_message_content=InputTextMessageContent(message_text=f"https://www.youtube.com/watch?v={result['id']}"),
        # input_message_content=InputTextMessageContent(message_text=f"{html.link(value=result['title'], link=f'https://www.youtube.com/watch?v={result['id']}')}"),
        # input_message_content = InputTextMessageContent(
        #     message_text=f"{html.link(value=result['title'], link='https://www.youtube.com/watch?v=' + result['id'])}"
        # ),
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
# 

# @dp.inline_query()
# async def inline_handler(inline_query: types.InlineQuery):
#     text = inline_query.query
#     asyncio.sleep(1)
#     results = youtube_search(query=text)    
#     datas = [InlineQueryResultArticle(
#         type='article',
#         id=str(uuid.uuid4()),
#         title=result['title'],
#         input_message_content=InputTextMessageContent(message_text=f"https://www.youtube.com/watch?v={result['id']}"),
#         description=f"{result['viewCount']['short']}\n{result['publishedTime']} {result['duration']}",
#         thumbnail_url=result['thumbnails'][0]['url'],
#         hide_url=True,
#     ) for result in results]
#     try:
#         await bot.answer_inline_query(
#             inline_query_id=inline_query.id,
#             results=datas,
#             cache_time=1,
#             is_personal=True,
#             switch_pm_parameter="add",
#             switch_pm_text="@YouTubSearchBot"
#         )
#     except:
#         pass
# def views_format(number):
#     number = int(number)
#     units = ['', 'K', 'M', 'G', 'T', 'P']
#     k = 1000.0
#     magnitude = int(floor(log(number, k)))
#     return '%.2f%s' % (number / k**magnitude, units[magnitude])

# def views_format(number):
#     # Sonni raqamga aylantirish va qiymatni floatga o'tkazish
#     number = float(number.replace(',', '').replace(' views', ''))
    
#     # Sonni unitlar (K, M, G, T, P) o'qib chiqarish uchun tayyorlash
#     units = ['', 'K', 'M', 'G', 'T', 'P']
    
#     # 1000-ga bo'lgan darajani aniqlash
#     k = 1000.0
    
#     # Sonning qanday ko'chirilishi kerakligini aniqlash
#     magnitude = int(floor(log(number, k)))
    
#     # Formatlash va qaytarish
#     return '%.2f%s' % (number / k**magnitude, units[magnitude])
# def views_format(number):
#     # Sonni raqamga aylantirish va qiymatni floatga o'tkazish
#     number = float(number.replace(',', '').replace(' views', ''))
    
#     # Sonni unitlar (K, M, G, T, P) o'qib chiqarish uchun tayyorlash
#     units = ['', 'K', 'M', 'G', 'T', 'P']
    
#     # 1000-ga bo'lgan darajani aniqlash
#     k = 1000.0
    
#     # Sonning qanday ko'chirilishi kerakligini aniqlash
#     magnitude = int(floor(log(number, k)))

#     formatted_number = '{:.2f}'.format(number / k**magnitude)
#     if formatted_number.endswith('.00'):
#         formatted_number = formatted_number[:-3]
#     return '{}{}'.format(formatted_number, units[magnitude])


# @dp.inline_query()
# async def inline_handler(inline_query:types.InlineQuery):
#     text = inline_query.query
#     results = youtube_search(query=text)
#     datas = [
#         InlineQueryResultArticle(
#             type='article',
#             id=str(uuid.uuid4()),
#             title=result['title'],
#             input_message_content=InputTextMessageContent(message_text=f"https://www.youtube.com/watch?v={result['id']}"),
#         description=f"{views_format(result['views'])}\n{result['publish_time']}\n {result['duration']}",
#         thumbnail_url=result['thumbnails'][0],
#         hide_url=True,
#         ) for result in results]
#     await inline_query.answer(results=datas, cache_time=60,is_personal=True)
