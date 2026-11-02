# Capacités et choix du chemin de réalisation

Consulter cette page pour choisir un outil ou annoncer la portée d'une livraison. Les statuts s'appliquent à une opération précise, pas à tout Moodle.

## Lire les preuves

- **Construit et vérifié hors ligne** : opération exécutée sur fichiers ; préciser si un contrôle repose seulement sur une doublure. Aucune conclusion automatique sur Moodle.
- **Vérifié en instance** : préciser date, environnement et fonction réellement observée. Un succès rapporté par l'utilisateur reste signalé comme tel ; il ne valide pas un autre générateur.
- **Documenté seulement** : procédure ou modèle décrit, éventuellement observé dans une sauvegarde, mais pas exécuté dans le contexte cible. Préciser si l'automatisation reste à développer.

Les statuts ci-dessous sont datés du **2026-11-01**. Réviser la date et la portée lorsqu'une nouvelle preuve change le statut. Une documentation n'a pas besoin d'être rebaptisée « inconnue » parce qu'un générateur n'existe pas.

## Ce que la version 0.7.0 fournit

Le [parcours de cocréation](conception-cours.md) et le [modèle de base](modele-cours-de-base.md) définissent le résultat à préparer avec validation humaine. Leur statut est **documenté seulement** : ils ne modifient pas les possibilités effectives des scripts ci-dessous.

| Tâche et moyen | Prérequis | Statut au 2026-11-01 | Preuve et limites |
|---|---|---|---|
| Encoder : `scripts/encoder_videos.py` | Python ≥ 3.13, FFmpeg, source lisible | Construit et vérifié hors ligne | Encodage réel synthétique ; qualité perceptuelle à relire |
| Nettoyer : `scripts/nettoyer_vtt.py` | VTT simple, corrections de projet si nécessaires | Construit et vérifié hors ligne | Tests de formats/refus ; pas de transcription ni de relecture humaine remplacée |
| H5P : `scripts/construire_h5p.py` | Fiches, médias, .mbz de référence TAR/gzip, bibliothèques adaptées ; FFmpeg ou affiches | Construit et vérifié hors ligne | Huit paquets reconstruits, contre-vérifiés indépendamment ; IV/QS et MultiChoice, TrueFalse, DragText seulement |
| UUID H5P stables, ajout 3a | `cle` unique par question/interaction, identifiant de fiche conservé | Construit et vérifié hors ligne | `content.json` identique sur deux constructions ; insertion/réorganisation sans modifier les autres UUID. Sans clé : avertissement et UUID aléatoire ; effet sur tentatives non essayé |
| Langue des sous-titres, ajout 3a | Code/libellé de fiche ou replis CLI ; VTT source fourni | Construit et vérifié hors ligne | Piste, libellé et fichier adaptés ; défaut français conservé ; aucune traduction ni preuve de lecture Moodle |
| Extraire, remplacer, réemballer : `scripts/mbz_archive.py` | TAR/gzip, sortie neuve, temporaire court | Construit et vérifié hors ligne | Contrôles de format et conservation ; extraction/réemballage employés par la chaîne restaurée en M1, sans garantie de transformation métier universelle |
| Aperçu : `scripts/inspect_mbz.py` | Archive TAR, lecture autorisée | Construit et vérifié hors ligne | Tests synthétiques ; limites de parcours et métadonnées dans [sauvegardes.md](sauvegardes.md) |
| Refuser une base distante ou absente, ajout 3a | `--validation-locale`, `wwwroot` local, `dbhost` local explicite et socket conforme | Construit et vérifié hors ligne par doublure PHP seulement | Refus avant élévation/construction ; après bootstrap de `config.php`. Ni connexion réelle ni isolation complète démontrées |
| Créer un cours : `scripts/moodle/construire_cours.php` | Instance/base locales isolées et autorisées, état de secours, contrat v1 à v4 | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | H5P/Page/Fichier éprouvés en M1 ; Livre/Devoir, banque/test et profils v4 ci-dessous. Cours neuf masqué, collision refusée |
| Livre avec chapitres HTML, ajout M2a | Contrat v2, fichiers de chapitre sous le projet | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Deux chapitres dont un secondaire, sauvegarde/restauration, contenu et navigation apprenant. Pas d'import de médias incorporés |
| Devoir individuel texte/fichier, ajout M2a | Contrat v2, note/seuil, grille ou guide explicites | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Trois canaux de remise, grilles et guide restaurés ; remises et correction sous comptes fictifs via API natives, états attente/échec/réussite, retour visible. Groupes, dates, annotations et cycles de nouvelle remise hors profil |
| Vérifier H5P/Page/Fichier et attestation : `scripts/moodle/verifier_cours.php` | Instance locale isolée, [contrat version 1](contrat-structure.md), deux comptes fictifs préparés | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Cours construit puis restauré ; notes réelles 0/100 et 100/100, achèvements 3/2 et API de restriction. Parcours et PDF essayés séparément ; autres versions non garanties |
| Feedback : construction et vérification, ajout M2c | Contrat v4, composants natifs ; [profil](contrat-parcours-v4.md) | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Deux modes d'anonymat, cinq types d'éléments ; construction/sauvegarde/restauration, formulaire incomplet refusé, complet accepté, répétition refusée et achèvement. Anonymat de restitution natif, sans garantie d'anonymisation de la base |
| Leçon non notée avec branchements, ajout M2c | Contrat v4, pages/choix/sauts ; [profil](contrat-parcours-v4.md) | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Pages de contenu et choix unique, sauts remappés après restauration, parcours navigateur d'une branche jusqu'à END et achèvement. Autres pages/notation/reprises hors profil |
| Attestation créée dans l'instance, ajout M2c | Contrat v4, Custom certificate, PNG et condition de réussite précédente | Vérifié en instance : Moodle 5.1.8+ local / Custom certificate 5.0.11, 2026-11-01 | Profil une page/fond/nom/date/code ; restauration, deux étudiants fictifs, refus/accès réels et PDF avec fond identique pixel pour pixel. Aucun modèle institutionnel riche ni signature repris |
| Vérifier Questionnaire : même script | Contrat version 1, plugin présent | Construit et vérifié hors ligne par doublure PHP seulement | Aucun générateur Questionnaire ; pas de validation de son API réelle |
| Banque qbank et test natif, ajout M2b | Moodle 5.1, contrat v3, quatre types natifs ; [profil](contrat-tests-natifs.md) | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Cinq questions couvrant choix unique/multiple, vrai/faux, courte et numérique ; construction/sauvegarde/restauration et références vérifiées. Deux tentatives par API natives sous étudiant fictif : 5/7 puis 7/7, achèvements 3/2, tolérance dedans/dehors. Interface et autres types non éprouvés |
| Questionnaire et autres activités hors profils ci-dessus | Droits et composants cibles ; procédures des familles | Documenté seulement | Modèles observés et sources ; pas de générateur générique inclus |
| Intégrer des H5P déjà présents dans un .mbz, ajout 3b | TAR/gzip, modules/sections visibles, paquet intégré unique ; [procédure](retouches-activites.md) | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Huit iframes rendus après restauration ; suivi du questionnaire essayé via son activité source. Sept vidéos non jouées jusqu'au bout ; pas de généralisation du suivi intégré |
| Ajouter une attestation dans un .mbz, ajout 3b corrigé en M1 | Modèle customcert explicite à une page/fond PNG, contexte de cours déclaré, condition de réussite ; [procédure](retouches-activites.md) | Vérifié en instance : Moodle 5.1.8+ local, Custom certificate 5.0.11, 2026-11-01 | Restauration, refus après échec, accès après réussite et PDF ouvert dans le navigateur avec fond ; pixels du fond identiques. Ne couvre pas tous les modèles/versions |
| Images de logo/signature dans Custom certificate, ajout 3c | PNG intégrés référencés par le modèle, profil documenté | Construit et vérifié hors ligne | Copie d'une signature depuis un modèle réel, SHA-1 et références contrôlés ; rendu PDF et restauration non essayés |
| Sauvegarder : `scripts/moodle/sauvegarder_cours.php`, ajout 3c | Instance locale isolée, cours masqué, sortie neuve et exclusions possibles | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | Export natif sans utilisateurs, avec fichiers, puis restauration. Pas de dépendance réelle à la banque de contenus dans cet essai ; contenu à trier avant partage |
| Restaurer et essayer le cours | Instance autorisée, composition voulue, composants disponibles | Vérifié en instance : Moodle 5.1.8+ local, 2026-11-01 | CLI natif Moodle, cours neuf, deux apprenants fictifs et PDF ; aucun script générique de restauration supplémentaire livré dans la skill |

Les tests et la reconstruction de 2b, la refonte documentaire, 3a, 3b, 3c et leurs correctifs ont été contre-validés indépendamment le 2026-11-01 (80 tests). M1 a ensuite éprouvé la portée ci-dessus en instance locale et corrigé l'en-tête XML et le contexte des images : 82 tests, contre-validation indépendante acquise. M2a ajoute Livre/Devoir, éprouvés dans la portée indiquée : 90 tests et contre-validation indépendante acquise. M2b ajoute banque/test natif : 103 tests et contre-validation indépendante acquise. M2c ajoute Feedback/Leçon/attestation native dans la portée indiquée : 114 tests réussis et contre-validation indépendante acquise. Les pièces restent dans le projet de développement, sans chargement ordinaire pour construire un cours. Une approbation hors ligne ne prouve pas l'usage Moodle.

## Règles de conception et limites des moyens

L'[outil de choix](modele-cours-de-base.md#choisir-les-activités) et [Concevoir une section](concevoir-section.md) guident le parcours, avec statut **documenté seulement, 2026-11-02**. Ils ne modifient pas les scripts. Choisir l'activité pour apprendre puis annoncer au responsable la voie réalisable. Glossaire, fichiers supplémentaires du Devoir, pratique sans correction et intégration H5P par défaut doivent encore être complétés ou éprouvés ; le contrôle automatique de l'expérience n'est pas encore fourni. La description riche et sa vérification doivent aussi être confirmées dans le contrat. Ne pas confondre recommandation éditoriale et capacité livrée.

## Choisir la réalisation

Pour un cours neuf, reprendre d’abord le modèle d’attestation approuvé. Préférer la création native puis sa sauvegarde seulement si son profil conserve ce modèle ou si l’adaptation a été validée. La retouche `.mbz` reste utile sans instance ou pour reprendre un modèle couvert plus riche, dont image/signature ; ne pas le réduire silencieusement au profil natif. Les deux chemins ont leurs propres preuves et limites.

1. Pour un plan, des textes ou des fichiers : travailler hors ligne ; isoler les conditions à vérifier à l'import.
2. Pour une activité sans générateur : utiliser l'interface si elle est disponible et autorisée. Pour répéter en nombre, examiner les fonctions réellement exposées avant de proposer un développement.
3. Pour reprendre une sauvegarde : préserver l'original, découvrir la structure et ses dépendances ; préférer la restauration native aux reconstructions XML improvisées.
4. Pour une fonctionnalité absente du site ou de l'outil : expliquer la limite et proposer une alternative répondant à l'objectif. Ne pas remplacer silencieusement un type spécialisé.

## Étendue du savoir repris du corpus

Les procédures couvrent aussi les ressources structurées, les banques natives, les travaux, les enquêtes, la collaboration, les parcours à embranchements et la reconnaissance. La présence observée de nombreux types ne signifie ni que tous sont disponibles sur un site, ni qu'un cours doit tous les utiliser.

Les succès historiques rapportés sur H5P intégré et téléchargement d'une attestation servent d'indices contextualisés. Ils ne remplacent pas l'essai de nouveaux paquets, de nouvelles restrictions ou d'une nouvelle restauration. Aucun relevé global « tout testé » ou « rien testé » n'est approprié.
