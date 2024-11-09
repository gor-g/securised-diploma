# TP 2 INFO 002 - stéganographie, signature, etc.

## Gor Grigoryan et Julien Galerne

### Bibliothèques utilisées

- himage
- numpy
- pycryptodome
- argparse
- hashlib
- PIL

### Question 1

Usage : vous devez avoir sur votre PC une image à modifier, et un fichier .txt contenant le message

```sh
python3 main.py insert data/diplome-BG.png "Le mystère des Pyramides, c’est le mystère de la conscience dans laquelle on n’entre pas." data/tmp/diplome-BG_msg.png
python3 main.py extract data/tmp/diplome-BG_msg.png
```

### Question 2

_L'université cache (ou écrit en hexa dans un coin ou QR code) un message (signature) dans le diplôme, et publie la clé publique sur son site. Ainsi, tout le monde peut s'assurer que le diplôme est émis par l'université. La clé privée, pour chiffrer le message, est gardé secret par l'université._

### Question 3
Utilisation :
```sh
python3 main.py text ./data/diplome-BG.png "Ceci est du texte" ./data/tmp/output-text.png
```

### Question 4
Utilisation :
```sh
python3 main.py keygen 2048 "jg"
python3 main.py create "Truc BIDULE" "11/11/1111" 2024 14.65 "bien"
```

### Question 5
Utilisation :
```sh
python3 main.py verify "Truc BIDULE"
```

### Génération d'un diplôme
1. On écrit les infos en clair sur le diplôme (nom, moyenne, date de naissance, année...).
2. Les bits de poids faibles de l'image sont mis à zéro
3. L'image est ensuite hachée puis signée 
4. La signature est cachée dans le diplôme

### Vérification d'un diplôme
1. On récupère la signature cachée dans le diplôme
2. On nettoie les bits de poids faible du diplôme pour revenir à la même image qu'au point 2. de la génération du diplôme
3. On hache à nouveau l'image de la même manière qu'au point 3. de la génération du diplôme mais sans la signée.
4. On vérifie si la signature cachée correspond à l'empreinte de l'image avec la clé publique.