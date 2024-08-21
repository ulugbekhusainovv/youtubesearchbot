from aiogram import BaseMiddleware
from aiogram.types import Message,Update
from typing import *
from utils.misc.checksub import joinchat
from data.config import ADMINS


class UserCheckMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
    
        if isinstance(event, Message):
            user_id = str(event.from_user.id)

            if user_id not in ADMINS:
                is_member = await joinchat(event.from_user.id)
                if not is_member:
                    return
        return await handler(event, data)