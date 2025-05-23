
from typing import Any
from steganographer import Steganographer
from diploma import Diploma
from env_service import EnvService
from himage import imread # type: ignore
from utils import write_text
from PIL import Image
from Crypto.PublicKey import RSA

class Runner:
    def __init__(self) -> None:
        EnvService()

    def run(self, args: dict[str, Any]) -> Any:
        command = args.pop("command")
        print(f"running : {command}\nwith arguments : {args}")
        self.__getattribute__(command)(**args)

    @staticmethod
    def insert(image: str, message: str, output: str):
        """
        Hide a message in an image
        --------------------------
        image: str
            The path to the image to hide the message in (e.g. "image.png")
        message: str
            The message to hide in the image
        output: str
            The path to the output image (e.g. "output.png")
        --------------------------
        """
        steganographer = Steganographer()
        steganographer.set_im(imread(image))
        steganographer.set_msg(message)

        steganographer.write_msg()
        steganographer.export(output)

    @staticmethod
    def extract(image: str):
        """
        Read a message written with steganographer, from an image
        --------------------------
        image: str
            The path to the image to read the message from (e.g. "image.png")
        --------------------------
        Returns:
            The message read from the image
        --------------------------
        """
        print(Steganographer().set_im(imread(image)).read_msg())


    @staticmethod
    def text(template: str, message:str, output: str):
        """
        Write a visible message on an image
        --------------------------
        template: str
            The path to the template image (e.g. "template.png")
        message: str
            The message to write on the image
        output: str
            The path to the output image (e.g. "output.png")
        --------------------------
        """

        img = Image.open(template)
        img = write_text(img, message, (100, 100))
        img.save(output)

    @staticmethod
    def keygen(key_size:int, passphrase:str):
        EnvService().generate_keys(key_size, passphrase)

    @staticmethod
    def create(student:str, date_birth:str, year:int, average:float, merit:str):
        Diploma().create_diploma(EnvService.TEMPLATE_PATH, student, date_birth, year, average, merit)

    @staticmethod
    def verify(student: str):
        with open(EnvService.PUBLIC_KEY_PATH, "rb") as k:
            public_key = RSA.import_key(k.read())
        print(Diploma().verify_diploma(student, public_key))