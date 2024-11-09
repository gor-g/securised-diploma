
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

    def generate_signature(self, path_img: str):
        """Generate a signature for a given file and a given key"""

        h = self.hash_image(path_img)

        key = None
        while key is None:
            try:
                with open(self.env_service.PRIVATE_KEY_PATH, "rb") as f:
                    key = RSA.import_key(f.read(), passphrase=self.env_service.get_passphrase())
            except ValueError:
                print("Mot de passe incorrect")
                key = None

        signature = pkcs1_15.new(key).sign(h)

        return base64.b64encode(signature).decode()


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
        filled_diploma_im_path = self.env_service.get_diploma_output_path(student_name)
        img.save(filled_diploma_im_path)

        # we clean the LSBs before we generate the signature, so that when calling verify_signature
        # we know that we must call it on the image with a clean LSBs
        steganographer = Steganographer()
        steganographer.set_im(imread(filled_diploma_im_path))
        steganographer.clean_lsb()
        steganographer.export(filled_diploma_im_path)

        # sign file
        signature= self.generate_signature(filled_diploma_im_path)

        # HIDDEN
        steganographer = Steganographer()
        steganographer.set_im(imread(filled_diploma_im_path))
        steganographer.set_msg(signature)
        steganographer.write_msg()
        steganographer.export(filled_diploma_im_path)

        return img


    def verify_diploma(self, student: str, public_key:RsaKey):
        """Verify if the diploma is authentic. Get the hidden signature, remove it, and re-sign diploma to check if it's the same signature."""

        student_name = student.replace(" ", "_")
        im_path = self.env_service.get_diploma_output_path(student_name)
        nolsb_im_path = self.env_service.get_nolsb_diploma_tmp_path(student_name)

        # get the hidden signature
        steganographer = Steganographer()
        steganographer.set_im(imread(im_path))
        signature = steganographer.read_msg()

        # clean the LSBs to get the version of the image used to generate the signature
        steganographer.clean_lsb()
        steganographer.export(nolsb_im_path)

        # hash diploma to check if it's the same as the one used to generate the signature
        return self.check_signature(public_key, self.hash_image(nolsb_im_path), signature)
