
from steganographer import Steganographer
from env_service import EnvService
from himage import imread # type: ignore
from PIL import Image
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Hash import SHA256
from PIL import Image, ImageDraw, ImageFont


import base64


class Diploma:   
    
    def __init__(self) -> None:
        self.env_service = EnvService()
        self.font = ImageFont.truetype(self.env_service.FONT_PATH, self.env_service.FONT_SIZE)

    def hash_image(self, path_img: str):
        with open(path_img, "rb") as f:
            data = f.read()

        return SHA256.new(data)
    
    def write_text(self, img: Image.Image, text: list[str]):
        """Write text on an image"""
        draw = ImageDraw.Draw(img)
        curr_height = self.env_service.TEMPLATE_MARGIN
        for line in text:
            width = self.font.getlength(line)
            pos = ((img.width - width)/2, curr_height)
            draw.text(pos, line, (0, 0, 0), self.font)
            curr_height += self.font.size*2

        return img

    def generate_signature(self, path_img: str, path_key: str = "./data/private.pem", passphrase:str ="Clé sécurisée"):
        """Generate a signature for a given file and a given key"""

        h = self.hash_image(path_img)

        with open(path_key, "rb") as f:
            key = RSA.import_key(f.read(), passphrase=passphrase)

        signature = pkcs1_15.new(key).sign(h)

        return base64.b64encode(signature).decode(), key


    def check_signature(self, public_key:RsaKey , h_img: "pkcs1_15.Hash", signature:str):

        bin_signature:bytes = base64.b64decode(signature)

        try:
            pkcs1_15.new(public_key).verify(h_img, bin_signature)
            print("Signature valide !")
            return True
        except ValueError:
            print("Signature invalide !")
            return False


    def create_diploma(self, template_path: str, student: str, date_birth: str, year: int, average: float, merit: str):
        """Create a diploma with visible and hidden informations"""
        
        img = Image.open(template_path)
        
        # VISIBLE
        text = [
            f" Université {'TRUCMACHIN'[::-1]}",
            f"Diplôme : Diplôme national de master en informatique",
            "",
            f"Session : {year}",
            f"Obtenu par : {student}",
            f"Né(e) le {date_birth}",
            "",
            f"Avec la moyenne de {average} / 20 et obtient donc la mention {merit.upper()}",
        ]
        img = self.write_text(img, text)
        student_name = student.replace(" ", "_")
        new_path = f"./data/diplome-{student_name}.png"
        img.save(new_path)

        # clean lsb (useful for the verify_diploma function)
        steganographer = Steganographer()
        steganographer.set_im(imread(new_path))
        steganographer.clean_lsb()
        steganographer.export(new_path)

        # sign file
        self.env_service.generate_keys(passphrase=student_name)
        signature, key = self.generate_signature(new_path, passphrase=student_name)

        # HIDDEN
        steganographer = Steganographer()
        steganographer.set_im(imread(new_path))
        steganographer.set_msg(signature)
        steganographer.write_msg()
        steganographer.export(new_path)

        return img, key.public_key()


    def verify_diploma(self, student: str, public_key:RsaKey):
        """Verify if the diploma is authentic. Get the hidden signature, remove it, and re-sign diploma to check if it's the same signature."""

        student_name = student.replace(" ", "_")
        path = f"./data/diplome-{student_name}.png"
        check_path = f"./data/diplome-{student_name}-check.png"

        # get and remove hidden signature
        steganographer = Steganographer()
        steganographer.set_im(imread(path))
        signature = steganographer.read_msg()
        steganographer.clean_lsb()
        steganographer.export(check_path)

        # hash diploma to check if it's the same as his signature
        return self.check_signature(public_key, self.hash_image(check_path), signature)
