import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в файле .env")

dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Это Lost & Found City Bot.\n\n"
        "Здесь можно искать потерянные вещи "
        "и сообщать о найденных.\n\n"
        "Команды:\n"
        "/lost — сообщить о потере\n"
        "/found — сообщить о находке\n"
        "/help — помощь"
    )


@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Чтобы сообщить о вещи, используйте /lost или /found.\n"
        "Поиск объявлений будет добавлен следующим этапом."
    )


@dp.message(Command("lost"))
async def lost_handler(message: Message):
    await message.answer(
        "Создание объявления о потерянной вещи "
        "будет реализовано на следующем этапе."
    )


@dp.message(Command("found"))
async def found_handler(message: Message):
    await message.answer(
        "Создание объявления о найденной вещи "
        "будет реализовано на следующем этапе."
    )


async def main():
    bot = Bot(token=TOKEN)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
