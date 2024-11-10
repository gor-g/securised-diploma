# Présentation d'un prototype pour la génération de diplômes numériques sécurisés
*Gor GRIGORYAN* 

*Julien GALERNE*

## Problématique
Afin de créer des versions numérique de diplôme infalsifiables, nous avons développer un petit prototype répondant à cette problématique.

Un diplôme contient un certain nombre d'informations qui, combinées ensemble, le rendent unique. En effet, il est inscrit le nom et prénom de l'étudiant, sa moyenne et sa date de naissance. Autant de données à caractères personnel qui peuvent être reliées à une seule personne.

Cependant, puisque ces diplômes sont au format numérique (image), ils pourraient être modifiés avec un logiciel d'édition d'image afin de changer la moyenne de l'étudiant par exemple.

C'est pourquoi nous vous proposons la solution suivante.

## Solution
Pour répondre à cette problématique, nous générons d'abord le diplôme en bonne et due forme. Les informations de l'étudiant sont incrites sur le diplôme à savoir :
- son nom
- sa moyenne (et sa mention)
- sa date de naissance

Les autres informations présentes sur le diplôme sont :
- le nom de l'université
- le nom du diplôme
- la session

Tout cela est écrit en clair sur le diplôme et la combinaison de toutes ces informations le rendent unique.
*Les bits de poids faible de l'image sont mis à zéro, ce qui nous servira plus tard.*

Ensuite, le diplôme est haché avec un algorithme de hachage. Cela génère une empreinte pour notre image, qui est à son tour signée à l'aide d'un algorithme de cryptographie asymétrique.
La clé privée est connue seulement par l'université alors que la clé publique est disponible pour tout le monde.

Nous obtenons donc une signature unique pour notre diplôme.

Celle-ci est ensuite cachée dans le diplôme. Pour cela, on met à zéro les bits de poids faible de l'image, ce qui nous permet d'utiliser ces bits pour cacher notre signature.
C'est cette version du diplôme, avec la signature cachée, qui est ensuite envoyée à l'étudiant.

Maintenant, pour vérifier l'authenticité du diplôme, il faut extraire la signature cachée dans le diplôme.
Ensuite, les bits de poids faible sont remis à zéro et l'image du diplôme est hachée à nouveau.
Enfin, la signature extraite est comparée avec la nouvelle empreinte de l'image en utilisant le clé publique.

**Si le moindre pixel de cette image a été modifié, la nouvelle empreinte de l'image ne coincidera pas avec la signature extraite et le diplôme perdra son authenticité.**

### Génération du diplôme
![Schéma génération diplôme](./generation-diplome.png "Génération du diplôme")

### Vérification du diplôme
![Schéma vérification diplôme](./verification-diplome.png "Vérification d'un diplôme")

## Choix techniques
Pour réaliser ce prototype, nous avons utilisé le langage de programmation Python. Il contient de nombreuses bibliothèques utiles pour la cryptographie et la manipulation d'images. De plus, il est possible de faire tourner cette solution sur un serveur, avec un framework de développement web tel que Flask.

Afin de généner le diplôme, nous utilisons la bibliothèque de manipulation d'image `Pillow`.

Pour cacher et récupérer des informations dans une image, nous utilisons les librairies `numpy` et `himage`.

L'algorithme de hachage utilisé est SHA-256 et la signature est générée à l'aide de l'algorithme de cryptographie asymétrique RSA.
Tout cela est disponible dans la bibliothèque `pycryptodome`.

Tout cela permet donc de faire tourner notre prototype sur un serveur Flask de l'université, où l'utilisateur enverrait l'image sur ce serveur ainsi que la clé publique afin de vérifier l'authenticité du diplôme.

## Documentation
Les deux points les plus importants du prototype sont la création du diplôme et sa vérification.
### Création du diplôme
Tout d'abord, nous avons la fonction de création d'un diplôme
```py
def create_diploma(self, template_path: str, student: str, date_birth: str, year: str, average: str, merit: str):
    """Create a diploma with visible and hidden informations"""
```
Cette fonction prend en paramètre le chemin de l'image de fond du diplôme, le prénom et le nom de l'étudiant, sa date de naissance, l'année d'obtention du diplôme, sa moyenne ainsi que sa mention.

Ensuite, l'image de fond du diplôme est ouverte et les informations sont inscrites dessus en clair.
```py  
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
```
L'image du diplôme est ensuite sauvegardée dans un nouveau fichier png.

L'étape suivante consiste en mettre à zéro les bits de poids faible de l'image pour pouvoir la signer puis y cacher cette signature.
```py 
# we clean the LSBs before we generate the signature, so that when calling verify_signature
# we know that we must call it on the image with a clean LSBs
steganographer = Steganographer()
steganographer.set_im(imread(filled_diploma_im_path))
steganographer.clean_lsb()
steganographer.export(filled_diploma_im_path)
```

Puis, le diplôme est signé.
```py 
# sign file
signature= self.generate_signature(filled_diploma_im_path)
```

Enfin, on cache la signature du diplôme dans l'image.
```py 
# HIDDEN
steganographer = Steganographer()
steganographer.set_im(imread(filled_diploma_im_path))
steganographer.set_msg(signature)
steganographer.write_msg()
steganographer.export(filled_diploma_im_path)

return img
```

### Vérification du diplôme
Ensuite, nous avons une fonction pour vérifier l'authenticité d'un diplôme.
```py
def verify_diploma(self, student: str, public_key:RsaKey):
    """Verify if the diploma is authentic. Get the hidden signature, remove it, and re-sign diploma to check if it's the same signature."""
```
La fonction prend en paramètre le nom de l'étudiant (sous la forme Prénom NOM) ainsi que la clé publique pour vérifier la signature.

La fonction récupère ensuite la signature dans le diplôme et crée une copie du diplôme, avec les bits de poids faible remis à zéro.
```py
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
```

La copie du diplôme est ensuite hachée puis la signature extraite est comparée avec cette empreinte à l'aide de la clé publique afin de vérifier l'authenticité du diplôme.
```py
# hash diploma to check if it's the same as the one used to generate the signature
return self.check_signature(public_key, self.hash_image(nolsb_im_path), signature)
```

### Signature d'un fichier
Afin de signer notre diplôme, on utilise la fonction suivante :
```py
def generate_signature(self, path_img: str):
    """Generate a signature for a given file"""
```

L'image est d'abord hachée :
```py
h = self.hash_image(path_img)
```
On obtient alors une empreinte qui ressemble à cela :
```sh
Empreinte de "./data/diplome-Truc_BIDULE.png" = f92c8515656b7bcb8687e2c8a1d1c7dee7b0c36bf3f186b99522744ce1e77eb4
```

Puis, on récupère la clé privée de l'université.
```py
key = None
while key is None:
    try:
        with open(self.env_service.PRIVATE_KEY_PATH, "rb") as f:
            key = RSA.import_key(f.read(), passphrase=self.env_service.get_passphrase())
    except ValueError:
        print("Mot de passe incorrect")
        key = None
```

Enfin, l'empreinte du diplôme est signée avec la clé privée de l'université, selon les standards de cryptographie à clé publique RSA.
```py
signature = pkcs1_15.new(key).sign(h)
```

On retourne ensuite la signature encodée en base 64 et prête à être cachée dans notre diplôme.
```py
return base64.b64encode(signature).decode()
```
```sh
Signature de "./data/diplome-Truc_BIDULE.png" = EqdTTkdPsbNGi8mTBw04S8TiJsRHgaHWDJof9JT3WIpfCyyaInQh/vrGOLFm1qb0w4iRL+B+pz4UubP1mE+FVn+WmTVsyllIjD+Q/QqtmzDvfUtt/htZRh/k8gK/yAdHQW1ORnMoDIaz99Rldr5rZulqiEM7r9Y5nmFLJly9D6mLV11jAK9qzmli1eXkqUZjN2CoL/xX+rbiIU95RDNRUa3uW88uR/MONOTV4EsDnMboFXadMlxh30Ze0DrwqynzYs/E6304kKlPBYOKx8LnZmWUtXt3LtEU+E1zifetfNUhIzvrQS7dQ5o04qQsnmFJOm0bpsIj/82p9X/slKVd1g==
```

## Conclusion
En conclusion, on a ici une manière simple et efficace d'authentifier notre diplôme. La modification du moindre pixel de cette image entrainera la génération d'une empreinte totalement différente, rendant la signature invalide lors de la vérification.

Pour mettre en place ce service, il est raisonnable de pouvoir implémenter un serveur web Flask, avec une route qui redirige l'utilisateur vers un formulaire. Sur celui-ci, on téléverse notre copie numérique du diplôme et le serveur détermine (avec la procédure susrelatée) si le fichier est authentique ou non.