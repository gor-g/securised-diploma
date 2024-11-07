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

Tout cela est écrit en clair sur le diplôme et rend la combinaison de toutes ces informations le rendent unique.
*Les bits de poids faible de l'image sont mis à zéro, ce qui nous servira plus tard.*

Ensuite, le diplôme est haché avec un algorithme de hachage. Cela génère une empreinte pour notre image qui est à son tour signée à l'aide d'un algorithme de cryptographie asymétrique.
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
Pour réaliser ce prototype, nous avons utilisé le langage de programmation Python. Il contient de nombreuses bibliothèques utiles pour la cryptographie et la manipulation d'images. De plus, il est possible de faire tourner cette solution sur un serveur avec un framework de développement web tel que Flask.

Afin de généner le diplôme, nous utilisons la bibliothèque de manipulation d'image `Pillow`.

Pour cacher et récupérer des informations dans une image, nous utilisons les librairies `numpy` et `himage`.

L'algorithme de hachage utilisé est SHA-256 et la signature est générée à l'aide de l'algorithme de cryptographie asymétrique RSA.
Tout cela est disponible dans la bibliothèque `pycryptodome`.

Tout cela permet donc de faire tourner notre prototype sur un serveur Flask de l'université, où l'utilisateur enverrait l'image sur ce serveur ainsi que la clé publique afin de vérifier l'authenticité du diplôme.

## Documentation
Voici les deux points les plus importants du prototype.
### Création du diplôme
Tout d'abord, nous avons la fonction de création d'un diplôme
```py
def create_diploma(template_path: str, student: str, date_birth: str, year: str, average: str, merit: str):
    """Create a diploma with visible and hidden informations"""
```
Cette fonction prend en paramètre le chemin de l'image de fond du diplôme, le prénom et le nom de l'étudiant, sa date de naissance, l'année d'obtention du diplôme, sa moyenne ainsi que sa mention.

Ensuite, l'image de fond du diplôme est ouverte et les informations sont inscrites dessus en clair.
```py  
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
```
L'image du diplôme est ensuite sauvegardée dans un nouveau fichier png.

L'étape suivante consiste en mettre à zéro les bits de poids faible de l'image pour pouvoir la signer puis y cacher cette signature.
```py 
# clean lsb (useful for the verify_diploma function)
steganograph = Steganograph()
steganograph.set_im(imread(new_path))
steganograph.clean_lsb()
steganograph.export(new_path)
```

Puis, le diplôme est signé.
```py 
# sign file
generate_keys(passphrase=student_name)
signature, key = sign_file(new_path, passphrase=student_name)
```

Enfin, on cache la signature du diplôme dans l'image.
```py 
# HIDDEN
steganograph = Steganograph()
steganograph.set_im(imread(new_path))
steganograph.set_msg(signature)
steganograph.write_msg()
steganograph.export(new_path)

return img, key.public_key()
```

### Vérification du diplôme
Ensuite, nous avons une fonction pour vérifier l'authenticité d'un diplôme.
```py
def verify_diploma(student: str, public_key):
    """Verify if the diploma is authentic. Get the hidden signature, remove it, and resign diploma to check if it's the same signature."""
```
La fonction prend en paramètre le nom de l'étudiant (sous la forme Prénom NOM) ainsi que la clé publique pour vérifier la signature.

La fonction récupère ensuite la signature dans le diplôme et crée une copie du diplôme, avec les bits de poids faible remis à zéro.
```py
student_name = student.replace(" ", "_")
path = f"./data/diplome-{student_name}.png"
check_path = f"./data/diplome-{student_name}-check.png"

# get and remove hidden signature
steganograph = Steganograph()
steganograph.set_im(imread(path))
signature = steganograph.read_msg()
steganograph.clean_lsb()
steganograph.export(check_path)
```

La copie du diplôme est ensuite hachée puis la signature extraite est comparée avec cette empreinte à l'aide de la clé publique afin de vérifier l'authenticité du diplôme.
```py
# hash diploma to check if it's the same as his signature
return check_signature(public_key, hash_image(check_path), signature)
```

## Conclusion
En conclusion, on a ici une manière simple et efficace d'authentifier notre diplôme. La modification du moindre pixel de cette image entrainera la génération d'une empreinte totalement différente, rendant la signature invalide lors de la vérification.

Pour mettre en place ce service, il est raisonnable de pouvoir mettre en place un serveur web Flask, avec une route qui dirige l'utilisateur vers un formulaire. Sur celui-ci, on téléverse notre copie numérique du diplôme et le serveur nous dit si le fichier est authentique ou non.