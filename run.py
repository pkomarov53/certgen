import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from bot.settings import TOKEN, ADMIN_ID
from bot.connection import DB_CONFIG, get_connection, init_db, save_cert,check_user_exists
from bot.utilities import generate_certificate

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Введи свои ФИО, чтобы получить именной сертификат.")

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user is None:
        return
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM certificates")
            result = cursor.fetchone()
            count = result['cnt'] if result else 0
            await message.answer(f"📊 Всего выдано сертификатов: {count}")
    except Exception as e:
        await message.answer(f"Ошибка БД: {e}")
    finally:
        conn.close()

@dp.message(Command("gen"))
async def admin_generate_manual(message: Message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        return

    name_to_gen = message.text.replace("/gen", "").strip() if message.text else ""

    if not name_to_gen:
        await message.answer("⚠️ Ошибка: Напишите ФИО после команды. Пример: `/gen Иван Иванов`")
        return

    status = await message.answer(f"🛠 Админ-режим: Генерирую сертификат для `{name_to_gen}`...")
    
    try:
        path, cert_num = generate_certificate(name_to_gen)
        
        await message.answer_photo(
            FSInputFile(path), 
            caption=f"✅ Сертификат создан вручную!\nФИО: {name_to_gen}\nНомер: {cert_num}"
        )
        
        # Удаляем временный файл
        if os.path.exists(path):
            os.remove(path)
            
    except Exception as e:
        await message.answer(f"❌ Ошибка при ручной генерации: {e}")
    finally:
        await status.delete()

@dp.message(F.text)
async def handle_name(message: Message):
    if not message.text or not message.from_user:
        return

    # Проверка: не получал ли пользователь сертификат ранее?
    existing_cert = check_user_exists(message.from_user.id)
    if existing_cert:
        await message.answer(f"Вы уже получили сертификат! Ваш номер: {existing_cert['cert_number']}")
        return

    status = await message.answer("⏳ Генерирую...")
    try:
        path, cert_num = generate_certificate(message.text)
        save_cert(message.from_user.id, message.text, cert_num)
        
        await message.answer_photo(FSInputFile(path), caption=f"Готово! Номер: {cert_num}")
        os.remove(path)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
    finally:
        await status.delete()

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
