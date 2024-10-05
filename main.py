import os
import asyncio
import logging
import requests
import feedparser
import html2text
import aiogram
import pickle
import os.path
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

subs = {}

def load_subs():
    global subs
    if os.path.isfile("subs"):
        with open("subs", "rb") as f:
            subs = pickle.load(f)
    else:
        with open("subs", "wb") as f:
            pickle.dump(subs, f)


def save_subs():
    global subs
    with open("subs", "wb") as f:
        pickle.dump(subs, f)


def sub(userId, link):
    global subs
    if userId in subs and not link in subs[userId]:
        subs[userId].append(link)
    else:
        subs[userId] = [link]
    with open("subs", "wb") as f:
        pickle.dump(subs, f)


def unsub(userId, link):
    global subs
    if link in subs[userId]:
        subs[userId].remove(link)
        with open("subs", "wb") as f:
            pickle.dump(subs, f)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global subs
    userId = message.from_user.id
    if userId in subs:
        await message.answer("С возвращением!\nПросто вставьте сюда ссылку для добавления в подписки и напишите /news для просмотра новостей")
    else:
        subs[userId] = []
        save_subs()
        await message.answer("Здравствуйте!\nПросто вставьте сюда ссылку для добавления в подписки и напишите /news для просмотра новостей")


@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    sent = await message.answer("Ожидайте...")
    entries = []
    userId = message.from_user.id
    for link in subs[userId]:
        feed = feedparser.parse(link, sanitize_html=True)
        entries.append(feed.entries[0])
    await sent.delete()
    for entry in entries:
        title = entry.title
        try:
            summary = html2text.html2text(entry.summary)
        except AttributeError:
            summary = ''
        link = entry.link
        await message.answer(f"{title}\n\n{summary}\n{link}", parse_mode="Markdown")


@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    global subs
    reply = "\n".join(subs[message.from_user.id])
    await message.answer(reply)


@dp.message()
async def link(message: types.Message):
    global subs
    link = message.text
    userId = message.from_user.id
    if link in subs[userId]:
        unsub(userId, link)
        await message.reply("Подписка отменена")
    else:
        sub(userId, link)
        await message.reply("Подписано")


async def main():
    load_subs()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
