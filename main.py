import argparse
from steganographer import Steganograph
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

# args = vars(parser.parse_args())

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
        return True
    except ValueError:
        print("Signature invalide !")
        return False


def create_diploma(template_path: str, student: str, date_birth: str, year: str, average: str, merit: str):
    """Create a diploma with visible and hidden informations"""
    
    img = Image.open(template_path)
    
    # VISIBLE
    img = write_text(img, f"Université {'TRUCMACHIN'[::-1]}", (345, 150))
    img = write_text(img, "Diplôme national de master en informatique".upper(), (210, 200))
    img = write_text(img, f"Session : {year}", (400, 235))
    img = write_text(img, f"Obtenu par : {student}", (345, 300))
    img = write_text(img, f"Né(e) le {date_birth}", (390, 350))
    img = write_text(img, f"Avec la moyenne de {average} / 20 et obtient donc la mention {merit.upper()}", (160, 420))

    student_name = student.replace(" ", "_")
    new_path = f"./data/diplome-{student_name}.png"
    img.save(new_path)

    # clean lsb (useful for the verify_diploma function)
    steganograph = Steganograph()
    steganograph.set_im(imread(new_path))
    steganograph.clean_lsb()
    steganograph.export(new_path)

    # sign file
    generate_keys(passphrase=student_name)
    signature, key = sign_file(new_path, passphrase=student_name)

    # HIDDEN
    steganograph = Steganograph()
    steganograph.set_im(imread(new_path))
    steganograph.set_msg(signature)
    steganograph.write_msg()
    steganograph.export(new_path)

    return img, key.public_key()


def verify_diploma(student: str, public_key):
    """Verify if the diploma is authentic. Get the hidden signature, remove it, and resign diploma to check if it's the same signature."""

    student_name = student.replace(" ", "_")
    path = f"./data/diplome-{student_name}.png"
    check_path = f"./data/diplome-{student_name}-check.png"

    # get and remove hidden signature
    steganograph = Steganograph()
    steganograph.set_im(imread(path))
    signature = steganograph.read_msg()
    steganograph.clean_lsb()
    steganograph.export(check_path)

    # hash diploma to check if it's the same as his signature
    return check_signature(public_key, hash_image(check_path), signature)


def main():
    # hide_message()

    import sys
    if len(sys.argv) <= 1:
        print("Aucun argument entré, usages ci-dessous :", end="\n\n")
        print(f"Ecrire du texte sur une image : {sys.argv[0]} text ./data/diplome-BG.png \"Ceci est du texte\" ./data/output-text.png", end="\n\n")
        print(f"Générer un diplôme : {sys.argv[0]} create \"Truc BIDULE\" \"11/11/1111\" 2024 14.65 \"bien\"", end="\n\n")
        print(f"Vérifier un diplôme : {sys.argv[0]} verify \"Truc BIDULE\"", end="\n\n")
        return
    
    if sys.argv[1] == "text":
        if len(sys.argv) != 5:
            print(f"usage: {sys.argv[0]} text ./data/diplome-BG.png \"Ceci est du texte\" ./data/output-text.png")
            return
        
        img = Image.open(sys.argv[2])
        img = write_text(img, sys.argv[3], (100, 100))
        img.save(sys.argv[4])
    
    elif sys.argv[1] == "create":
        if len(sys.argv) != 7:
            print(f"usage: {sys.argv[0]} create \"Truc BIDULE\" \"11/11/1111\" 2024 14.65 \"bien\"")
            return
        
        img, key = create_diploma("./data/diplome-BG.png", sys.argv[2], 
                                    sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        
    elif sys.argv[1] == "verify":
        if len(sys.argv) != 3:
            print(f"usage: {sys.argv[0]} verify \"Truc BIDULE\"")
            return
        
        with open("./data/public.pem", "rb") as k:
            public_key = RSA.import_key(k.read())
        print(verify_diploma(sys.argv[2], public_key))

    else:
        return
        # student = "Truc BIDULE"
        # img, key = create_diploma("./data/diplome-BG.png", student, "11/11/1111", "2024", "14.65", "bien")

        # with open("./data/public.pem", "rb") as k:
        #     public_key = RSA.import_key(k.read())
        # print(verify_diploma(student, public_key))

main()