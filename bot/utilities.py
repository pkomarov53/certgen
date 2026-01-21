import random
from PIL import Image, ImageDraw, ImageFont
from bot.settings import TEMPLATE_PATH, FONT_PATH, FONT_SIZE

def generate_certificate(name: str):
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    cert_id = f"CERT-{random.randint(100000, 999999)}"
    
    # Центрирование текста
    draw.text((img.width // 2, img.height // 2 - 20), name, font=font, fill="black", anchor="mm")
    draw.text((img.width // 2, img.height - 150), f"№ {cert_id}", font=font, fill="gray", anchor="mm")
    
    path = f"temp_{cert_id}.png"
    img.save(path)
    return path, cert_id