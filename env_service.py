
from Crypto.PublicKey import RSA
import os


class EnvService:
    DATA_ROOT = "./data"
    TMP_DIR_PATH = f"{DATA_ROOT}/tmp"
    PRIVATE_KEY_PATH: str = f"{TMP_DIR_PATH}/private_key.pem"
    PUBLIC_KEY_PATH: str = f"{TMP_DIR_PATH}/public_key.pem"
    
    TEMPLATE_PATH: str = f"{DATA_ROOT}/diplome-BG.png"
    FONT_PATH: str = f"{DATA_ROOT}/Marianne-Bold.otf"
    TEMPLATE_MARGIN: int = 150
    FONT_SIZE: int = 20

    def __init__(self) -> None:
        os.makedirs(self.TMP_DIR_PATH, exist_ok=True)

    def generate_keys(self, key_size:int, passphrase:str):
        """Generate a public key and a private key in 2 files : `public.pem` and `private.pem`"""

        key = RSA.generate(key_size)
        private_key = key.export_key(passphrase=passphrase)
        with open(self.PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_key)

        public_key = key.public_key().export_key()
        with open(self.PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_key)

    def get_passphrase(self)->str:
        return input("enter the passphrase to decrypte the private key : \n")

    def get_diploma_output_path(self, student_name:str)->str:
        return f"{self.TMP_DIR_PATH}/diplome-{student_name}.png"
    
    def get_nolsb_diploma_tmp_path(self, student_name:str)->str:
        return f"{self.TMP_DIR_PATH}/diplome-nolsb-{student_name}.png"