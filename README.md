# TP 2 INFO 002 - stéganographie, signature, etc.

## Gor Grigoryan et Julien Galerne

### Bibliothèques utilisées

- himage
- numpy
- pycryptodome
- argparse
- hashlib

### Question 1

Usage : vous devez avoir sur votre PC une image à modifier, et un fichier .txt contenant le message

```sh
python3 main.py -i data/diplome-BG.png -o data/diplome-BG_msg.png -m data/msg.txt
```

### Question 2

L'université cache (ou écrit en hexa dans un coin ou QR code) un message (signature) dans le diplôme, et publie la clé publique sur son site. Ainsi, tout le monde peut s'assurer que le diplôme est émis par l'université.
La clé privée, pour chiffrer le message, est gardé secret par l'université.
