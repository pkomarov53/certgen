import asyncio
import random
import os
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from PIL import Image, ImageDraw, ImageFont

# --- НАСТРОЙКИ ---
TOKEN = ""
TEMPLATE_PATH = "template.jpg"
FONT_PATH = "font.ttf"
FONT_SIZE = 60

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            cert_number TEXT UNIQUE,
            issue_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_certificate(user_id, name, cert_number):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO certificates (user_id, full_name, cert_number, issue_date) VALUES (?, ?, ?, ?)",
        (user_id, name, cert_number, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

# --- ЛОГИКА ГЕНЕРАЦИИ ---
def generate_certificate(name: str):
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    
    # Генерируем уникальный номер
    cert_id = f"CERT-{random.randint(100000, 999999)}"
    
    # Координаты (настройте под свой шаблон)
    draw.text((img.width // 2, img.height // 2), name, font=font, fill="black", anchor="mm")
    draw.text((img.width // 2, img.height - 150), f"№ {cert_id}", font=font, fill="gray", anchor="mm")
    
    output_path = f"temp_{cert_id}.png"
    img.save(output_path)
    return output_path, cert_id

# --- БОТ ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Введите ФИО для получения сертификата:")

@dp.message(F.text)
async def handle_name(message: Message):
    # Проверяем, что есть и текст, и данные пользователя
    if message.text is None or message.from_user is None:
        return

    # Теперь Pylance видит, что message.from_user точно существует (не None)
    user_id = message.from_user.id 
    user_full_name = message.text

    status_msg = await message.answer("⏳ Генерирую и записываю в базу...")
    
    try:
        # Генерация
        file_path, cert_number = generate_certificate(user_full_name)
        
        # Сохранение (теперь user_id гарантированно число)
        save_certificate(user_id, user_full_name, cert_number)
        
        photo = FSInputFile(file_path)
        await message.answer_photo(
            photo, 
            caption=f"Ваш сертификат успешно выдан!\nНомер: {cert_number}"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        await status_msg.delete()

async def main():
    init_db() # Создаем таблицу при запуске
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
