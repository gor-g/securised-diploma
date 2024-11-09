from PIL import Image, ImageDraw, ImageFont
from env_service import EnvService

def fread(file: str):
    with open(file, "r") as f:
        content = f.read()
    return content


def write_text(img: Image.Image, text: str, pos: tuple[int, int]):
    """Write text on an image"""
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(EnvService.FONT_PATH, EnvService.FONT_SIZE)
    draw.text(pos, text, (0, 0, 0), font)

    return img