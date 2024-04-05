from aiogram.filters import Command
from loader import dp
from aiogram import types
@dp.message(Command('help'))
async def help_bot(message:types.Message):
    await message.answer(f"What kind of help do you need?\n"
                          f"Basic commands: \n/start - Restart Bot\n"
                          f"/help - Help\n/stat - Bot statistics")
