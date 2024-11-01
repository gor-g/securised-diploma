Doit contenir :

- les choix fonctionnels faits (choix de l'information cachée, présentation des informations "techniques", ...) et leur justification,
    - le fait de signer l'empreinte de l'image rendra toute modification de l'image impossible
    - Problème : où stocker cette signature ?
        - dans l'image : si qqu'un modifie l'image, la signature sera tjs la même, cachée dans l'image.
        Solution : on extrait la signature de l'image (reset des LSB) lors d'une vérification et on compare celle-ci avec la signature de la nouvelle image sans stéganographie
        - sur un serveur ?
- les choix technologiques faits (langage, algorithme de signature, bibliothèques) et recommandations pour le produit final,
- description "haut niveau" de votre solution,
- documentation de vos programmes / fonctions / scripts, ...
- conclusion sur la faisabilité et l'intérêt du service.
