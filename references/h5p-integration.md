# H5P : intégrer le contenu et vérifier son suivi

Pour fabriquer les paquets, lire [chaine-video-h5p.md](chaine-video-h5p.md). Pour les notes et restrictions, compléter avec [suivi-reconnaissance.md](suivi-reconnaissance.md).

Pour intégrer hors ligne des activités déjà présentes dans une sauvegarde, utiliser la [procédure de retouche H5P](retouches-activites.md), avec son profil et ses refus ; l'insertion dans l'éditeur ci-dessous reste la voie à tester dans le site.

## Défaut de conception

Pour un entraînement sans conséquence, afficher le H5P **dans la description de section**, avec activité source furtive si le site le permet. Exemple : question et retour sur la page de travail ; contre-exemple : ressource séparée imposant un aller-retour pour pratiquer. Choisir note et suivi selon le besoin, sans créer un enjeu évaluatif par défaut. Les évaluations formatives et sommatives privilégient le [test natif](tests-questions.md).

La retouche d'une sauvegarde est un moyen déjà fourni ; son application reste explicite et limitée par son profil. L'intégration automatique dès la construction n'est pas annoncée par cette règle documentaire. Vérifier les capacités actuelles avant de promettre le résultat.

## Choisir l'objet source

Un paquet `.h5p` est un fichier de contenu ; la banque de contenus est un lieu d'édition/stockage ; `h5pactivity` est une activité Moodle. Une intégration dans une Page ou une section est un mode de présentation. Choisir l'activité source et le mécanisme de suivi selon le besoin, au lieu d'inférer une note de la seule présence d'un H5P affiché.

La chaîne fournie construit Interactive Video et Question Set avec trois interactions internes. D'autres conteneurs et contenus sont observés : Course Presentation, Column, Interactive Book, Accordion, Image Hotspots, Three Image, Single Choice Set, Drag Question et Drag Text. Leur édition doit passer par un outil qui gère leurs versions ; le générateur inclus ne les prend pas tous en charge.

## Intégrer dans une section avec une activité source

1. Créer ou repérer une véritable activité H5P contenant le paquet voulu. Conserver ses réglages de tentatives, de note et d'achèvement.
2. Si l'affichage dans la section est souhaité, rendre l'activité disponible sans affichage direct sur la page du cours lorsque le site permet ce mode. Ne pas la rendre inaccessible à l'apprenant.
3. Utiliser l'insertion H5P offerte par l'éditeur pour référencer le paquet de cette activité source. Ne pas créer sans nécessité une deuxième copie de la banque dont on supposerait le même suivi.
4. Dans le montage local observé, l'éditeur stockait un marqueur `h5p-placeholder` et le filtre « Display H5P » assurait le rendu. Aucun `data-tag-id` n'était stocké ; ne pas en inventer.
5. Vérifier avec un apprenant lecture, sous-titres, interactions et remise finale, puis regarder tentative, note et achèvement séparément.

Représentation du marqueur, **pas un HTML prêt à coller** :

```html
<div class="h5p-placeholder" contenteditable="false">[ADRESSE_DU_PAQUET_DE_L_ACTIVITE_SOURCE]</div>
```

L'adresse dépend de la zone `mod_h5pactivity/package`, des contextes et fichiers du site. La retrouver à partir de l'objet source ou de l'éditeur ; ne pas recopier un identifiant d'un autre cours. Les classes d'espacement dépendent des styles disponibles.

## Résoudre un défaut de suivi

Relever l'activité source exacte et distinguer : aucune tentative, tentative sans score, score sans note, note sans achèvement, ou simple affichage non rafraîchi. Dans le cas rapporté, « Remettre vos réponses » puis une actualisation F5 permettaient de voir la coche ; cela ne prouve pas que F5 répare un envoi de note manquant.

Ne pas attribuer le rendu ou les traces à un plugin tiers sur la seule présence de son nom. Examiner la configuration réellement utilisée avant de diagnostiquer.

## Restaurer et retester

Après copie/restauration, rouvrir l'intégration et vérifier qu'elle atteint le paquet du cours destination. Les adresses absolues `pluginfile.php` peuvent conserver des contextes anciens ; si nécessaire, réinsérer par l'éditeur. Vérifier ensuite accès, remise et suivi sans dépendre du cours source.

**Preuves :** montage et achèvement rapportés par un concepteur, complétés par les observations de sauvegardes. Ni une intégration arbitraire, ni la portabilité de toute adresse, ni tous les chemins xAPI ne sont validés. [Activité H5P](https://docs.moodle.org/501/en/H5P_activity), [activités furtives](https://docs.moodle.org/501/en/Stealth_activities), [filtres](https://docs.moodle.org/501/en/Filters).

## Essai complémentaire U2

2026-11-03 : Question Set d’entraînement intégré par le constructeur v5 dans une section puis sauvegardé/restauré. Réponse et fin dans le navigateur sous apprenant ont produit une tentative, un score et un achèvement. Activité source furtive et marqueur remappé contrôlés ; aucune conclusion nouvelle sur le visionnage intégral des vidéos ou toutes les bibliothèques. Voir [le contrat v5](contrat-experience-v5.md).
