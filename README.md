# Moodle Course Builder — 0.7.0

Une skill en français pour les conseillers pédagogiques et les enseignants qui souhaitent concevoir, construire et vérifier des cours Moodle avec une IA. Elle réunit une démarche de cocréation, des procédures à consulter selon la tâche, des exemples fictifs et des outils de fabrication. Elle n'est ni un plugin Moodle ni un constructeur universel.

## Une démarche avec validation humaine

Le travail suit les phases conception, brouillon, maquettes, finalisation, essai (4b), mise en production et maintenance. La personne responsable valide chaque passage ; des phases peuvent être fusionnées sur sa décision. Pour une petite modification, seules les phases pertinentes sont reprises.

Une section pilote permet de valider le contenu puis la direction visuelle avant de décliner le cours. Pour une nouvelle direction, l'IA propose deux ou trois variantes. Chaque section dispose ensuite d'une maquette HTML sur écran et mobile ; une forme allégée exige un accord humain. L'expérience utilisateur et l'accessibilité guident le choix des composants du thème.

Le **socle par défaut** comprend l'accueil, l'explication de l'achèvement avant chaque activité requise, une évaluation finale avec seuil, une attestation après réussite et une rétroaction. Le plan confirme ce socle ou justifie les adaptations pour validation. Le contenu reste d’abord dans la description de section : H5P intégré pour s’entraîner sans conséquence, test natif autocorrigé pour évaluer, Devoir avec trace pour pratiquer, Glossaire pour le lexique. Page seulement pour une longue lecture, Livre rarement, Leçon à éviter. Reprendre par défaut direction visuelle et attestation du cours de référence approuvé ; l’expérience utilisateur se valide à chaque phase. Chaque choix indique la fabrication disponible et les manipulations manuelles nécessaires.

Les nouvelles règles de conception ne livrent pas automatiquement leurs extensions techniques : consulter les capacités ; les développements UX restent en cours, non publiés.

Voir [Concevoir une section](references/concevoir-section.md), [la démarche complète](references/conception-cours.md), [le modèle de base](references/modele-cours-de-base.md) et [l'exemple de plan](assets/exemple-plan-cours.md).

## Capacités et preuves

Les statuts sont datés et limités à des opérations précises dans [la matrice des capacités](references/capacites.md), qui fait référence.

| Fonction | État et portée |
|---|---|
| Encodage vidéo, nettoyage VTT, paquets H5P Interactive Video et Question Set | Vérifiés hors ligne, dont huit paquets reconstruits et comparés indépendamment. Les clés d'interaction stabilisent les identifiants ; la continuité des tentatives après mise à jour reste à essayer. |
| Création de cours locaux, sections, Pages, fichiers et activités H5P | Vérifiée en instance locale, puis par sauvegarde/restauration. Sept vidéos n'ont pas été jouées jusqu'au bout ; le suivi intégré ne bénéficie pas d'une validation générale. |
| Livre et Devoir individuel texte, fichier ou mixte | Vérifiés en instance : chapitres, grille ou guide, remise, correction, attente et réussite. Les fonctions de groupe et les cycles de nouvelle remise sont hors profil. |
| Banque qbank et test natif | Vérifiés en instance : choix unique/multiple, vrai/faux, réponse courte, numérique avec tolérance ; tentatives par API natives, notes et achèvement après restauration. Les autres types ne sont pas générés. |
| Feedback, Leçon et attestation native | Vérifiés en instance dans les profils du contrat v4 : formulaires et obligations, une branche de Leçon jusqu'à la fin, refus après échec et accès après réussite, PDF avec fond. |
| Retouches de copies .mbz : intégration H5P et attestation depuis modèle | Restauration et attestation simple éprouvées en instance. Les images de signature d'un modèle plus riche ont été contrôlées hors ligne seulement. |
| Sauvegarde et vérification locales | Exécutées en instance ; export sans utilisateurs, fichiers inclus, références restaurées et états d'accès contrôlés. Le contenu libre doit encore être trié avant partage. |
| Questionnaire, autres activités et types spécialisés | Procédures documentées ; aucune promesse de génération. Le contrôle Questionnaire reste testé par doublure. |

Les essais d'instance du 1er novembre 2026 ont utilisé Moodle **5.1.8+** et Custom certificate **5.0.11**, avec des comptes fictifs dans des cours masqués. Ils ne garantissent pas une autre version, un autre thème ou une installation de production. Le pack de langue installé n'a pas suffi à obtenir un affichage et une date PDF en français dans ces essais.

## Prérequis

La lecture de la skill et la conception documentaire ne demandent aucun serveur Moodle. Pour les outils, prévoir selon la tâche :

- **Python 3.13 ou plus récent**, pour les scripts Python et leurs tests ; ils utilisent la bibliothèque standard.
- **FFmpeg**, pour encoder les vidéos et produire les affiches ; la chaîne a été testée avec la version 7.1. Voir [la procédure vidéo/H5P](references/chaine-video-h5p.md) pour la provenance et `FFMPEG_EXE`.
- **PHP CLI** et une installation **Moodle 5.1 locale, isolée et autorisée**, pour les scripts sous `scripts/moodle/`. PHP doit satisfaire les exigences de la version Moodle installée. Les essais réels ont utilisé PHP 8.2.4 ; les tests par doublures, PHP 8.5.12. `PHP_BIN` sélectionne le binaire pour les tests.
- **Custom certificate**, compatible avec l'instance, pour les opérations d'attestation ; ce plugin n'est pas fourni.
- Pour H5P, les médias et une sauvegarde de référence autorisée contenant les bibliothèques compatibles. La skill ne fournit pas ces bibliothèques et ne les télécharge pas automatiquement.

Les scripts PHP sont des outils de validation locale avec privilèges : lire [leurs conditions d'exécution](references/automatisation.md) et [les contrats](references/contrat-structure.md) avant usage. Les contrats v1 à v4 restent pris en charge. Aucun outil, compte ou serveur n'est installé par la copie de cette skill.

## Installation dans un agent local

Copier **tout le dossier**, en le nommant `moodle-course-builder`, dans le dossier de skills de l'agent ; `SKILL.md` doit être directement à sa racine. Ne pas copier seulement ce fichier et ne pas ajouter un niveau de dossier supplémentaire.

| Agent | Emplacement personnel de la copie |
|---|---|
| Codex | `~/.agents/skills/moodle-course-builder/` |
| Claude Code | `~/.claude/skills/moodle-course-builder/` |

`~` représente le dossier personnel. Les installations limitées à un projet utilisent respectivement `.agents/skills/` et `.claude/skills/` dans ce projet. Vérifier les emplacements pris en charge par sa version dans les documentations officielles [Codex](https://developers.openai.com/codex/skills/) et [Claude Code](https://code.claude.com/docs/en/skills).

Ouvrir une nouvelle session et demander explicitement à l'agent d'utiliser `moodle-course-builder`, puis vérifier qu'il lit la démarche et les capacités pertinentes. La détection automatique dépend de l'agent et n'est pas garantie par les tests des scripts. L'installation dans un agent hébergé peut utiliser un autre mécanisme.

## Première utilisation et tests

Exemple de demande : « Utilise moodle-course-builder pour proposer le plan d'un cours de 45 minutes. Justifie les activités et distingue ce que tu peux fabriquer des créations manuelles. Attends ma validation avant le brouillon. »

Conserver les contenus, médias, décisions et sorties dans un **dossier de projet distinct**. Les exemples dans `assets/` sont fictifs ; les médias référencés doivent être fournis par le projet. Commencer par la référence utile dans [SKILL.md](SKILL.md), sans charger toute la documentation.

Depuis la racine de la skill, exécuter les tests sans créer de cache :

```text
python -B -m unittest discover -s tests -q
```

Configurer `FFMPEG_EXE` et `PHP_BIN` si les exécutables ne sont pas disponibles par leur nom. La suite comporte **114 tests** ; les tests dépendants d'outils absents peuvent être ignorés et doivent être signalés comme tels. Ce résultat hors ligne ne remplace pas l'essai d'un vrai parcours étudiant dans l'instance cible.

## Limites et diffusion

Les scripts refusent les profils qu'ils ne prennent pas en charge. Il n'existe pas d'exporteur universel de banque de questions ni de garantie de compatibilité avec tous les plugins. Le PDF, les restrictions, les notes et l'achèvement doivent être éprouvés dans leur contexte. Une maquette ou une coche dessinée ne prouve pas un comportement Moodle.

La création native convient aux cours neufs dont le profil est couvert ; la retouche d'une copie de sauvegarde reste utile pour certains modèles. Préserver les sources et les tentatives avant toute maintenance. La mise en production nécessite son autorisation propre ; préparer des fichiers n'y autorise pas.

Aucun cours réel, média source, compte ni secret n'est inclus. Une sauvegarde sans utilisateurs peut encore contenir des informations dans les textes ou les médias : la relire avant partage. Voir [les sources et la portée](references/sources-portee.md).

## Licence

Copyright (c) 2026 François Gagnon. Code et documentation distribués sous [licence MIT](LICENSE). Les logiciels, plugins, bibliothèques H5P et contenus importés conservent leurs propres licences et autorisations.
