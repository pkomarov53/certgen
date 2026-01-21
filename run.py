import asyncio
import random
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from PIL import Image, ImageDraw, ImageFont

# --- НАСТРОЙКИ ---
TOKEN = ""
TEMPLATE_PATH = "templates/child-sert.png"  # Путь к картинке-шаблону
FONT_PATH = "templates/default.ttf"          # Путь к шрифту
FONT_SIZE = 72

bot = Bot(token=TOKEN)
dp = Dispatcher()

def generate_certificate(name: str):
    # Загружаем шаблон
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)
    
    # Загружаем шрифт
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    
    # Генерируем уникальный номер (например: 2024-XXXX)
    cert_id = f"{datetime.now().year}-{random.randint(1000, 9999)}"
    
    # Координаты (нужно подобрать под ваш шаблон)
    name_pos = (img.width // 2, img.height // 2 - 30)
    id_pos = (img.width // 2, img.height - 100)
    
    # Пишем текст (anchor="mm" выравнивает по центру)
    draw.text(name_pos, name, font=font, fill="black", anchor="mm")
    draw.text(id_pos, f"ID: {cert_id}", font=font, fill="gray", anchor="mm")
    
    # Сохраняем временный файл
    output_path = f"cert_{cert_id}.png"
    img.save(output_path)
    return output_path

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Привет! Введи свои ФИО, и я пришлю тебе именной сертификат.")

@dp.message(F.text)
async def handle_name(message: Message):
    status_msg = await message.answer("Генерирую сертификат, подождите...")
    
    try:
        # Создаем сертификат
        file_path = generate_certificate(message.text)
        
        # Отправляем файл пользователю
        photo = FSInputFile(file_path)
        await message.answer_photo(photo, caption=f"Готово! Ваш личный сертификат, {message.text}.")
        
        # Удаляем временный файл
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        await status_msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())