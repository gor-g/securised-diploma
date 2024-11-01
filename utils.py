from Crypto.Hash import SHA256
from PIL import Image, ImageDraw, ImageFont

def fread(file: str):
    with open(file, "r") as f:
        content = f.read()
    return content

def hash_image(path_img: str):
    with open(path_img, "rb") as f:
        data = f.read()

    return SHA256.new(data)

def write_text(img: Image, text: str, pos: tuple[int, int]):
    """Write text on an image"""
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("./data/Marianne-Bold.otf", 20)
    draw.text(pos, text, (0, 0, 0), font)

    return img