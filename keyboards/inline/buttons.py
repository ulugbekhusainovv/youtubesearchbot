from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton,WebAppInfo
from aiogram.filters.callback_data import CallbackData

page_size = 10
import sqlite3


class CheckCallBack(CallbackData, prefix='ikb1'):
    check:bool


class BlockedUsersListPaginatorCallback(CallbackData, prefix='page3'):
    page: int
    action:str
    length:int

def get_blocked_users():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocked_users")
    blocked_users = cursor.fetchall()
    conn.close()
    return blocked_users

# Blocker users

def blocked_users_list_button(page:int=0):
    btn = InlineKeyboardBuilder()
    length = len(get_blocked_users())
    data = get_blocked_users()
    try:
        start = page * page_size
        finish = (page + 1) * page_size
        if finish > length:
            datas = data[start:length]
        else:
            datas = data[start:finish]
    except Exception:
        datas = []


    if datas:
        for block_user in datas:
            btn.row(InlineKeyboardButton(text=f"{block_user[1]} - {block_user[2]}",callback_data=f"block_user_{page}_{block_user[2]}"), width=2)

        btn.row(InlineKeyboardButton(text="🏠", callback_data='back_panel'))

        if page > 0:
            btn.row(
                InlineKeyboardButton(
                    text=f"⏪Orqaga", callback_data=BlockedUsersListPaginatorCallback(page=page, action='prev', length=length).pack()
                )
            )

        if page > 0 and finish < length:
            if page_size > 0:
                btn.row(InlineKeyboardButton(text=f"{page+1} of {length//page_size+1}➕", callback_data="add_block_user"))


        if finish < length:
            btn.row(
                InlineKeyboardButton(
                    text=f"⏭️Oldinga", callback_data=BlockedUsersListPaginatorCallback(page=page, action='next', length=length).pack()
                )
            )


        if finish < length:
            btn.row(
                InlineKeyboardButton(
                    text="📄 Oxirgi sahifa", 
                    callback_data=BlockedUsersListPaginatorCallback(page=length//page_size+1, action='last', length=length).pack()
                )
            )
        if page > 0 and finish < length:
            if page_size > 0:
                btn.adjust(*(tuple(1 for _ in range(page_size+1)) + (3,)))

        return btn.as_markup()
    else:
        btn.row(InlineKeyboardButton(text="Topilmadi", callback_data='back_panel'))
        btn.row(InlineKeyboardButton(text="Qo'shish", callback_data='add_block_user'))
        return btn.as_markup()
