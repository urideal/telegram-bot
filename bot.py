import asyncio
from telethon import TelegramClient, events
from openai import AsyncOpenAI
import os

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
PHONE_NUMBER = os.environ["PHONE_NUMBER"]
OPENROUTER_KEY = os.environ["OPENROUTER_KEY"]

tg_client = TelegramClient("session", API_ID, API_HASH)
ai_client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)

SYSTEM_PROMPT = "Ты — помощник-автоответчик. Отвечай кратко. Если не хватает информации — задай уточняющий вопрос."

@tg_client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.is_private and not event.out:
        async with tg_client.action(event.chat_id, "typing"):
            await asyncio.sleep(2)
            try:
                response = await ai_client.chat.completions.create(
                    model="openai/gpt-3.5-turbo",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": event.raw_text}]
                )
                await event.reply(response.choices[0].message.content[:4000])
            except Exception as e:
                await event.reply(f"Ошибка: {str(e)[:100]}")

async def main():
    await tg_client.start(phone=PHONE_NUMBER)
    print("✅ Бот работает!")
    await tg_client.run_until_disconnected()

with tg_client:
    tg_client.loop.run_until_complete(main())
