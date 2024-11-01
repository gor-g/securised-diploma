import argparse
from message import Steganograph
from himage import imread
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
import base64
from utils import fread, hash_image, write_text
from PIL import Image

parser = argparse.ArgumentParser(description="encode messages into pictures")

# parser.add_argument('-i', '--input', type=str, required=True, help='path to the image')
# parser.add_argument('-o','--output', type=str, required=True, help='path to the output image')
# parser.add_argument('-m', '--message', type=str, required=True, help='path to the message file')
# # parser.add_argument('-k', '--key', type=str, required=True, help='path to the message file')

args = vars(parser.parse_args())

def hide_message():
    """Hide a message into a picture"""
    stenograph = Steganograph()
    stenograph.set_im(imread(args["input"]))
    stenograph.set_msg(fread(args["message"]))

    stenograph.write_msg()
    stenograph.export(args["output"])

    print(f"Message initial : {stenograph.read_msg()}")


    stenograph_for_read = Steganograph()
    stenograph_for_read.set_im(imread(args["output"]))
    print(f"Message relu : {stenograph_for_read.read_msg()}")


def generate_keys(key_size=2048, passphrase="Clé sécurisée"):
    """Generate a public key and a private key in 2 files : `public.pem` and `private.pem`"""

    key = RSA.generate(key_size)
    private_key = key.export_key(passphrase=passphrase)
    with open("./data/private.pem", "wb") as f:
        f.write(private_key)

    public_key = key.public_key().export_key()
    with open("./data/public.pem", "wb") as f:
        f.write(public_key)


def sign_file(path_img: str, path_key: str = "./data/private.pem", passphrase="Clé sécurisée"):
    """Generate a signature for a given file and a given key"""

    h = hash_image(path_img)

    with open(path_key, "rb") as f:
        key = RSA.import_key(f.read(), passphrase=passphrase)

    signature = pkcs1_15.new(key).sign(h)

    return base64.b64encode(signature).decode(), key


def check_signature(public_key, h_img, signature):

    signature = base64.b64decode(signature)

    try:
        pkcs1_15.new(public_key).verify(h_img, signature)
        print("Signature valide !")
    except ValueError:
        print("Signature invalide !")


def create_diploma(path_image: str, student: str, average: str, merit: str):
    """Create a diploma with visible and hidden informations"""
    
    img = Image.open(path_image)
    
    img = write_text(img, "Diplôme national de master en informatique".upper(), (210, 200))
    img = write_text(img, f"Obtenu par : {student}", (345, 300))
    img = write_text(img, f"Avec la moyenne de {average} / 20 et obtient donc la mention {merit.upper()}", (160, 400))

    return img


def main():
    # hide_message()
    signature, key = sign_file("./data/diplome-BG.png")
    h_img = hash_image("./data/diplome-BG.png")
    check_signature(key.public_key(), h_img, signature)
    path = "./data/diplome_ecrit.png"
    img = create_diploma("./data/diplome-BG.png", "Truc BIDULE", "14.65", "bien")
    img.save(path)
    # generate_keys()

main()