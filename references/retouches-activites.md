# Retoucher les H5P et ajouter une attestation dans un .mbz

**Statut au 2026-11-01 : vérifié en instance locale Moodle 5.1.8+ / Custom certificate 5.0.11**, pour le profil et les limites indiqués dans [capacites.md](capacites.md). Scripts Python ≥ 3.13, sauvegardes TAR/gzip uniquement ; originaux préservés et sortie nouvelle obligatoire. Extractions en temporaires courts, indépendantes de l'emplacement du projet.

Ces opérations transforment des objets déjà décrits dans une sauvegarde ; elles ne créent pas un cours vide ni une banque de questions. Les fichiers contenant des données de participants restent privés et hors du dépôt.

## Intégrer les activités H5P existantes

```text
python scripts/integrer_h5p_sections.py entree.mbz sortie-integree.mbz
python scripts/integrer_h5p_sections.py entree.mbz sortie-integree.mbz --modules <id-dans-cette-sauvegarde> --ancre "<aside>"
```

Sans sélection, tous les `h5pactivity` sont ciblés. Le script découvre leur section, contexte et paquet dans les XML ; il vérifie le blob intégré par SHA-1 et taille, suit l'ordre de la séquence de section, insère le marqueur de paquet et règle `visibleoncoursepage=0` sans rendre l'activité indisponible. La valeur `--modules` désigne les identifiants du fichier fourni, pas ceux d'un autre cours.

Insertion en fin de résumé par défaut. `--ancre` est une chaîne HTML exacte choisie dans le projet ; elle doit apparaître une seule fois dans chaque section ciblée et l'insertion se fait avant elle. Aucun texte d'encadré pédagogique n'est codé dans la skill.

Le profil exige activités et sections visibles, résumé HTML et un paquet intégré unique dans `mod_h5pactivity/package`, item 0, chemin `/`. Il refuse paquet absent/ambigu, blob incohérent, séquences invalides, restriction d'achèvement vers un module absent, activité déjà furtive, intégration existante et ancre ambiguë. Il refuse aussi les restrictions d'accès d'une activité H5P ciblée : leur articulation avec une intégration en section doit être examinée plutôt que contournée automatiquement. Les autres liens de contexte sont conservés.

Les notes, tentatives et conditions d'achèvement ne sont pas réécrites. Le filtre, l'éditeur, le suivi et la résolution des contextes restent à essayer après restauration ; voir [h5p-integration.md](h5p-integration.md).

## Ajouter une attestation depuis une référence explicite

Le modèle de présentation et la version du plugin proviennent d'une activité `customcert` choisie dans une autre sauvegarde. Les contenus du modèle restent des données du projet, pas des constantes dans le script. Profil actuel : **une page, une image de fond PNG**, éléments `bgimage`, `image` (logo/signature PNG), `studentname`, `date` de délivrance, `code`, `text` ou `coursename`, avec éléments directement sous la page. Une autre structure/version doit être examinée ; aucun support universel de Custom certificate n'est annoncé.

Créer un fichier JSON dans le projet, par exemple :

```json
{
  "identifiant": "attestation-finale",
  "nom": "Attestation de réussite",
  "intro_html": "<p>Votre réussite vous permet de télécharger l'attestation.</p>",
  "section": {"numero": 2},
  "condition": {"idnumber": "evaluation-finale"},
  "fond": "medias/fond-attestation.png",
  "auteur": "",
  "licence": "allrightsreserved"
}
```

```text
python scripts/ajouter_certificat.py entree.mbz sortie-certificat.mbz --reference modele.mbz --modele "{\"type\":\"customcert\"}" --config certificat.json
```

La commande ci-dessus illustre les arguments ; adapter les guillemets JSON au shell. En PowerShell, utiliser par exemple `--modele '{"type":"customcert"}'`. Les chemins relatifs de `fond` sont résolus par rapport au JSON. Image limitée à 32 Mio, signature PNG vérifiée ; le script ne prouve ni son décodage ni sa qualité graphique. Auteur et licence sont configurables ; vérifier les droits avant partage. `horodatage` entier facultatif permet un essai reproductible ; sinon l'heure d'exécution est utilisée.

Sélecteurs exacts : section par `id`, `numero` ou `nom` ; activité par `id`, `idnumber`, `nom` ou `type`. Plusieurs champs sont combinés et doivent désigner un seul objet. Le nom du certificat et son identifiant logique doivent permettre de refuser une double application ; l'identifiant est écrit dans `idnumber`.

L'activité condition doit déjà être visible et configurée pour un achèvement automatique avec réussite (`completion=2`, `completionpassgrade=1`). Le script ne lui invente pas un seuil et ne modifie pas sa notation. Il configure l'accès de l'attestation par cette dépendance. Vérifier en instance les états échec/réussite et le PDF : la condition XML ne prouve pas l'admissibilité réelle.

Les nouveaux identifiants sont réservés au-dessus des identifiants entiers repérés dans les attributs/champs XML terminant par `id`, avec une limite de profil à 2³¹−1. Les nouveaux objets utilisent des valeurs disjointes : module, contexte, instance, modèle, page, éléments et fichier. Sont mis à jour : références du modèle/page/éléments et du fond JSON, séquence de section, déclaration/réglages d'activité de `moodle_backup.xml`, `files.xml`, blob et `inforef.xml`. Les anciens objets ne sont pas renumérotés.

**Contexte des images, corrigé après essai M1 :** l'activité et le template ont leur contexte de module, mais les fichiers `mod_customcert/image` et les données JSON des éléments image/fond doivent désigner le **contexte du cours**, découvert dans `information/original_course_contextid`. Le plugin restaure les images depuis ce contexte, puis remappe les éléments vers celui du cours restauré. Les placer dans le nouveau contexte de module peut donner un PDF sans fond, malgré des références XML cohérentes. Contexte de cours absent/invalide et nom d'image déjà présent dans cette zone de cours : refus. Le champ de résultat `contexte_images` distingue cette valeur de `contexte` du module. [Restauration du plugin](https://github.com/mdjnelson/moodle-mod_customcert/blob/v5.0.11/backup/moodle2/restore_customcert_stepslib.php).

**Images, ajout 3c :** seules les images explicitement référencées par les éléments `image` sont reprises depuis le modèle, par contexte/zone/item/chemin/nom exacts. Leur contexte source peut différer du contexte de l'activité ; aucun rapprochement au seul nom n'est fait. Profil `mod_customcert/image`, item 0, chemin `/`, PNG de 32 Mio maximum. SHA-1 et taille sont vérifiés avant copie ; références de contexte sont alignées sur le cours de destination et identifiants de fichiers renouvelés, `inforef` complété, ancien userid et métadonnées d'auteur non recopiés (valeurs de configuration utilisées). Deux éléments utilisant le même fichier partagent une copie. Fichier absent, ambigu, corrompu ou collision de nom avec le nouveau fond : refus. Les signatures sont des contenus du projet soumis à ses droits, jamais des exemples à publier dans la skill.

Une référence partielle d'attestation est admise : ses anciennes restrictions ne sont pas reprises, elles sont remplacées par la condition de destination. Les émissions antérieures sont retirées ; emails et émission automatique sont désactivés. Les rôles, notes et autres conteneurs d'usage sont créés vides. Un modèle aux champs ou éléments non gérés est refusé plutôt que copié aveuglément.

## Vérification et limites

Les tests synthétiques contrôlent allocation sans collision, liens ajoutés, variantes de sélecteurs, remises en ordre, refus et préservation des sources/sorties. Des essais ciblés sur des sauvegardes réelles comparent les huit marqueurs H5P et leurs modules ainsi que la définition, le module et le fichier de fond de l'attestation après remappage explicite des nouveaux identifiants. Pour cette dernière comparaison, le livrable comparé sert lui-même de modèle : cela éprouve la mécanique de copie/remappage, pas la création indépendante de son contenu. Un autre modèle réel avec signature éprouve la copie des images et de leurs références. Ce n'est pas une équivalence du cours complet : les sources réelles diffèrent aussi sur d'autres contenus. Les XML touchés sont resérialisés par ElementTree ; comparer leur structure normalisée, pas leurs seuls octets.

**Reconnaissance du format, corrigée en M1 :** le détecteur Moodle cherche littéralement la déclaration `<?xml version="1.0" encoding="UTF-8"?>` dans les 200 premiers octets de `moodle_backup.xml`. Des guillemets simples sont du XML valide mais ne passent pas cette détection. Le sérialiseur produit la déclaration compatible ; ne pas se limiter à comparer des XML normalisés. [Détecteur Moodle 5.1](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/backup/util/helper/convert_helper.class.php).

L'essai M1 a restauré la sauvegarde corrigée, rendu huit intégrations, contrôlé les deux états d'accès à l'attestation et ouvert son PDF avec fond. Le suivi a été essayé via le questionnaire source ; sept vidéos et les signatures n'ont pas été éprouvées jusqu'au rendu final. Les sorties doivent encore être essayées dans leur cible selon [conception-cours.md](conception-cours.md), phase 4b, puis déployées seulement selon [sauvegardes.md](sauvegardes.md). La présence d'un plugin dans la référence ne prouve ni son installation ni ses versions sur le site cible ; les polices, filtres et composants restent à vérifier. Les erreurs n'écrasent pas l'entrée ; les fichiers sources extraits ne sont modifiés que dans un temporaire privé.
