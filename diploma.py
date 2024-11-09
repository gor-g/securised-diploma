
from steganographer import Steganographer
from himage import imread # type: ignore
from utils import hash_image, write_text
from PIL import Image
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey.RSA import RsaKey

import base64


class Diploma:   
        
    def generate_keys(self, key_size:int = 2048, passphrase:str = "Clé sécurisée"):
        """Generate a public key and a private key in 2 files : `public.pem` and `private.pem`"""

        key = RSA.generate(key_size)
        private_key = key.export_key(passphrase=passphrase)
        with open("./data/private.pem", "wb") as f:
            f.write(private_key)

        public_key = key.public_key().export_key()
        with open("./data/public.pem", "wb") as f:
            f.write(public_key)


    def generate_signature(self, path_img: str, path_key: str = "./data/private.pem", passphrase:str ="Clé sécurisée"):
        """Generate a signature for a given file and a given key"""

        h = hash_image(path_img)

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
        steganographer = Steganographer()
        steganographer.set_im(imread(new_path))
        steganographer.clean_lsb()
        steganographer.export(new_path)

        # sign file
        self.generate_keys(passphrase=student_name)
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
        return self.check_signature(public_key, hash_image(check_path), signature)
