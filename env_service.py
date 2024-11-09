
from Crypto.PublicKey import RSA


class EnvService:
    DATA_ROOT = "./data"
    RSA_KEY_SIZE: int = 2048
    DEFAULT_PASSPHRASE: str = "default_passphrase"
    TEMPLATE_PATH: str = f"{DATA_ROOT}/diplome-BG.png"
    PRIVATE_KEY_PATH: str = f"{DATA_ROOT}/private_key.pem"
    PUBLIC_KEY_PATH: str = f"{DATA_ROOT}/public_key.pem"
    FONT_PATH: str = f"{DATA_ROOT}/Marianne-Bold.otf"
    FONT_SIZE: int = 20
    TEMPLATE_MARGIN: int = 150
    

    def generate_keys(self, key_size:int = 2048, passphrase:str = "Clé sécurisée"):
        """Generate a public key and a private key in 2 files : `public.pem` and `private.pem`"""

        key = RSA.generate(key_size)
        private_key = key.export_key(passphrase=passphrase)
        with open("./data/private.pem", "wb") as f:
            f.write(private_key)

        public_key = key.public_key().export_key()
        with open("./data/public.pem", "wb") as f:
            f.write(public_key)

