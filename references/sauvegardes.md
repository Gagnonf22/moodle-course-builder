# Examiner, retoucher et restaurer un .mbz

Lire pour exploiter une sauvegarde existante. Utiliser [mbz-retouches-locales.md](mbz-retouches-locales.md) pour le socle Python, et [qualite-validation.md](qualite-validation.md) pour l'essai après restauration.

## Parcours utilisateur sans serveur local

La skill ne demande aucune installation de Moodle local ni aucun serveur web à transporter. Les essais se font dans le Moodle existant de l'utilisateur, selon les droits et règles de son organisation.

1. Préparer hors ligne les contenus, ressources et paquets que les outils disponibles savent réellement produire. Livrer un `.mbz` seulement si une voie de fabrication compatible est disponible ; sinon, expliciter les créations manuelles nécessaires et fournir les fichiers utiles. Un plan JSON n'est pas une sauvegarde importable.
2. Joindre au livrable les composants requis, limites connues, consignes de restauration/import par l'interface et manipulations complémentaires. Prévoir un cours de test distinct autorisé ; si l'utilisateur n'a pas les droits nécessaires, faire intervenir la personne habilitée, sans demander un serveur personnel.
3. L'utilisateur restaure le `.mbz` ou importe les ressources dans ce cours de test. Ne pas remplacer un cours avec participants pour un simple essai. L'agent n'envoie rien au site sur la seule autorisation de préparer les fichiers.
4. Fournir une fiche d'essai adaptée au parcours : navigation, médias, remise, résultats, achèvement, restrictions, attestation si présente, clavier et mobile. Décrire les actions et résultats attendus avec les cas pertinents de réussite, d'échec et de condition manquante.
5. Recueillir observations, messages d'erreur et captures utiles, sans identifiants, secrets ou traces de participants réels ; corriger puis faire réessayer les fonctions touchées. Sans retour, annoncer « À valider dans le Moodle cible », même après un succès de développement local.

Pour le Glossaire v5, le script local de reprise est réservé au développement. La skill ne livre pas encore de fichier d'import natif des termes testé sur le site cible : annoncer ce manque, fournir les définitions et prévoir leur saisie manuelle ou une autre voie d'import vérifiée. Ne pas demander l'exécution de PHP ni l'accès au serveur de l'utilisateur pour contourner cette limite.

## Identifier la bonne source

Relever chemin privé, taille, SHA-256 et rôle : cours complet, version précédente, export partiel ou collection de modèles. Deux fichiers de même nom peuvent contenir des cours différents. Garder l'original intact et écrire les sorties sous de nouveaux noms ; ne pas déduire la provenance d'un numéro de cours seul.

Ne pas publier la sauvegarde ou ses extraits par défaut : elle peut contenir des participants, tentatives, réponses et journaux. Pour apprendre une structure, lire uniquement les objets nécessaires ; ne pas reprendre les anciennes données d'usage dans les modèles génériques.

## Examiner au bon niveau

| Question | Pièces à rapprocher dans les archives concernées |
|---|---|
| Quel cours, quelle version, export complet ou partiel ? | Métadonnées de sauvegarde et options d'export, objets réellement présents |
| Quel parcours ? | Sections, séquences, modules, disponibilité, liens et contenu des résumés |
| Quelles questions sont effectivement utilisées ? | Banque, versions principales, emplacements du test, références fixes/dynamiques |
| Quels fichiers sont transportés ? | `files.xml`, blobs de contenu, zones de fichiers et références aux dépôts |
| Quels objets sont requis ? | Conditions d'accès/achèvement, sources de jeux, sauts de leçon, grilles et modèles |
| Que manque-t-il au compteur de modules ? | Blocs, badges et autres objets de cours à examiner séparément |

Un H5P intégré dans une section peut s'appuyer sur une activité source disponible sans affichage direct. La présence de deux objets n'est pas nécessairement une duplication pédagogique.

Une entrée de fichier sans blob peut être une référence vers la banque de contenus ou un dépôt. Distinguer cette dépendance d'une corruption ; la référence ne garantit toutefois pas sa résolution sur un nouveau site. Vérifier les blobs présents avec leur empreinte de contenu si l'intégrité est en question.

L'aperçu rapide inclus est limité :

```text
python scripts/inspecter_mbz.py entree.mbz
```

Il accepte TAR lisible par Python et produit des compteurs, sans extraction. Les préfixes `./` sont normalisés et les alias ambigus refusés ; il ne traite pas toutes les structures de métadonnées et ne remplace pas les rapprochements ci-dessus. Il peut sous-compter d'autres structures et omettre le format réel ; un résultat vide ou `null` ne prouve pas leur absence. L'option `--output` exige une sortie neuve. L'ancien inventaire détaillé et l'ancien empaqueteur ne sont pas livrés dans cette distribution, en raison de défauts connus non corrigés.

## Retoucher une copie

Choisir un temporaire court ; sous Windows, une arborescence profonde peut échouer même si le fichier semble exister. Précontrôler le format et les limites, puis extraire avec l'aide fournie lorsqu'elle convient. Ne pas renommer une extension pour rendre un format compatible.

Avant un ajout d'objet, relever les identifiants existants et les domaines d'identifiants concernés ; attribuer sans collision et mettre à jour toutes les références utiles. Un identifiant de module, de contexte, d'activité ou de question n'est pas interchangeable. Les [scripts de retouche H5P/attestation](retouches-activites.md) réalisent les profils explicitement décrits ; le réemballeur seul ne réalise aucune transformation métier.

Appliquer la transformation prévue, comparer le contenu et contrôler XML, séquences, fichiers et dépendances. Une chaîne remplacée exactement une fois est une garantie locale, pas une validation de l'ensemble du graphe Moodle. Réemballer sous une nouvelle sortie. Conserver les empreintes et le relevé de transformation dans le projet.

## Sauvegarde et restauration natives

Dans un environnement autorisé, sélectionner les objets et données nécessaires ; pour un modèle destiné à la réutilisation ou au partage, exclure les données des participants. Distinguer ce modèle de la sauvegarde privée de retour arrière décrite ci-dessous. Sauvegarder par les moyens natifs du site, puis vérifier la composition obtenue. Un export partiel doit être annoncé comme tel.

Le [sauvegardeur CLI local](automatisation.md) fournit un profil sans données d'utilisateurs, contrôlé par doublure seulement. Le [contrat de vérification](contrat-structure.md) décrit les contrôles après restauration, dont les restrictions de l'attestation pour deux comptes d'essai ; ils ne remplacent pas le parcours navigateur ni le contrôle du PDF.

Restaurer d'abord dans un cours de validation distinct lorsque les effets sont incertains. Vérifier le mode de restauration, les composants requis et les avertissements avant toute fusion/remplacement. Après restauration, relever les nouveaux objets, essayer liens, médias et parcours. Une restauration dite terminée ne prouve pas les fonctions du cours. [Sauvegarde](https://docs.moodle.org/501/en/Course_backup), [restauration](https://docs.moodle.org/501/en/Course_restore).

### Mise en production et cours avec participants

Privilégier la restauration dans un **nouveau cours**. Avant une restauration ou mise à jour en production, obtenir l'autorisation explicite de la personne responsable pour la cible et l'opération précises ; sauvegarder le cours existant et définir un retour adapté. L'approbation d'un plan, d'une maquette ou d'un essai n'autorise pas ce déploiement.

Pour un cours ayant des participants, examiner les effets sur contenus, tentatives, notes et achèvements. Moodle distingue la restauration avec fusion et celle qui supprime le contenu du cours destination : cette distinction est confirmée dans la [documentation Moodle 5.1, « General restore defaults »](https://docs.moodle.org/501/en/Course_restore#General_restore_defaults), consultée le 2026-11-01.

Une restauration qui **supprime le contenu existant** peut faire perdre les traces associées aux activités supprimées. L'autorisation doit nommer explicitement cette option. La sauvegarde préalable doit inclure les données des participants nécessaires au retour, avec une couverture vérifiée et un emplacement privé autorisé. Les possibilités d'inclusion dépendent des droits et réglages : voir [sauvegarde de cours](https://docs.moodle.org/501/en/Course_backup#Backing_up_a_course). Si ces conditions ne peuvent être établies, ne pas effectuer l'opération destructive ; privilégier un nouveau cours ou solliciter l'administrateur autorisé.

L'existence des modes fusion/suppression et des options de sauvegarde utilisateur est documentée ; aucun essai destructif ni récupération de données n'a été exécuté ici. La sauvegarde privée de retour n'est jamais un contenu à joindre à la skill ou au dépôt public.

**Portée :** compréhension du format et contrôles locaux ; aucune garantie générale de restauration inter-version ou de résolution des dépôts externes.
