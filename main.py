import argparse
from message import Steganograph
from himage import imread
from Crypto.PublicKey import RSA
from utils import fread

parser = argparse.ArgumentParser(description="encode messages into pictures")

parser.add_argument('-i', '--input', type=str, required=True, help='path to the image')
parser.add_argument('-o','--output', type=str, required=True, help='path to the output image')
parser.add_argument('-m', '--message', type=str, required=True, help='path to the message file')
# parser.add_argument('-k', '--key', type=str, required=True, help='path to the message file')

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

def main():
    hide_message()
    # generate_keys()

main()