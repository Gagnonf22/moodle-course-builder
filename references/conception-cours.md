# Cocréer un cours : phases et validations

Pour créer un cours, suivre cette démarche par défaut avec le [modèle de base](modele-cours-de-base.md). Pour une correction ponctuelle, reprendre seulement les phases et vérifications concernées. Cette procédure de domaine ne remplace pas les instructions générales de collaboration.

## Valider les passages

À chaque phase, annoncer ce qui est prêt, ce qui reste provisoire, la validation attendue et la suite. Présenter les choix à trancher et les écarts au plan ou au modèle. La personne responsable du cours valide avant la suivante. Consigner dans le `DECISIONS.md` du projet, ou son équivalent : date, phase, éléments approuvés et réserves. Son identité reste dans le projet, pas dans la skill.

Les phases peuvent être fusionnées sur décision humaine, avec une validation couvrant explicitement leurs livrables. Une approbation de plan ou de maquette n'autorise pas la mise en production. Reprendre la validation touchée lorsqu'un changement modifie l'expérience approuvée, le sens du contenu ou les règles de note, d'achèvement ou d'accès. Une coquille sans effet sur ces éléments n'exige pas de recommencer le parcours.

## 1. Conception

Créer ou reprendre un **dossier de projet propre au cours**, hors de la skill : sources, `DECISIONS.md`, `ROADMAP.md` et livrables ; réutiliser l’organisation existante sans la dupliquer. Les notes au responsable restent dans ce dossier, jamais dans le cours. Reprendre les sources, décisions et contenus existants. Définir public, prérequis, objectifs observables, durée indicative, contraintes du site et ressources disponibles. Relier chaque objectif à une action, une trace et une rétroaction : un quiz seul ne démontre pas nécessairement une compétence pratique.

Écrire le plan des sections et activités. Confirmer le socle du modèle de base — accueil, achèvement expliqué avant chaque activité requise, évaluation finale avec seuil, attestation après réussite et rétroaction — ou justifier son adaptation pour validation.

Pour le contenu des sections, appliquer l’[outil de choix des activités](modele-cours-de-base.md#choisir-les-activités) et [Concevoir une section](concevoir-section.md) : description de section d’abord, entraînement H5P intégré, évaluation par test natif, pratique avec Devoir et trace, lexique en Glossaire ; éviter la Leçon et les sous-niveaux. Justifier chaque choix par l'apprentissage visé, pas par la seule présence d'un générateur. Pour chaque élément, indiquer ce que la skill fabrique réellement et ce qui doit être créé manuellement dans Moodle ; signaler les prérequis ou développements manquants. Distinguer notamment fabrication d'un paquet H5P et création/configuration de son activité Moodle. Choisir une forme autre qu'une vidéo n'est pas un écart au socle.

### Tableau obligatoire avant construction

Livrable de phase 1 : **une ligne par activité ou ressource**, identifiée dans la première colonne ; distinguer les objets au lieu de regrouper test, attestation et rétroaction sur une seule ligne.

| Type Moodle exact (élément identifié) | Pourquoi cet outil : objectif et règle de choix | Alternative écartée et raison | Condition d'achèvement | Fabriqué par la skill ou à créer à la main |
|---|---|---|---|---|
| Devoir (`assign`) — Réaliser et vérifier | Pratiquer et remettre une trace | Page à coche manuelle : aucune remise réelle | À la remise, sans correction obligatoire | Profil v5 de pratique sans note et fichiers de consigne ; prérequis et essais du cours à vérifier |

**La construction ne commence qu'après validation de ce tableau par la personne responsable.** Consigner l'approbation avec sa portée dans le projet. Le brouillon et les maquettes suivent leurs validations propres ; un choix d'activité ne vaut pas autorisation de déploiement.

**Tout changement d'outil ultérieur, même pendant la construction, lui revient avant exécution** : présenter la raison, l'alternative, les effets sur l'achèvement et le mode de fabrication, mettre à jour la ligne concernée et attendre sa décision. Une incapacité du script n'autorise pas un remplacement. Voir le [tableau rempli](../assets/exemple-plan-cours.md).

Choisir une **section pilote** représentative d’une difficulté réelle. Reprendre **par défaut la direction visuelle et le modèle d’attestation du cours de référence approuvé** ; sans référence, prévoir l’exploration d’une direction nouvelle. Ne pas remplacer le modèle approuvé par un profil plus simple sans validation. Préciser les inconnues techniques ; ne pas bloquer la conception hors ligne faute d'accès au site.

**Contrôle UX :** KISS et peu d’écrans ; activités choisies pour apprendre ; titres compréhensibles ; séparation apprenant/responsable ; contenu spécifique à chaque étape. Exemple : un Devoir regroupe consigne et trace ; contre-exemple : trois activités pour un même atelier.

**À valider :** tableau obligatoire par activité/ressource, socle confirmé ou écarts justifiés, choix du parcours et leur justification, répartition fabrication/manipulations manuelles, section pilote, modalités de suivi et contraintes ouvertes. Voir l'[exemple synthétique](../assets/exemple-plan-cours.md).

## 2. Brouillon fonctionnel

Préparer les activités et ressources réelles de la section pilote : contenu, consignes, questions, réponses/rétroactions, documents, action attendue et conditions d'achèvement. Livrer les fichiers importables réellement réalisables et les opérations manuelles annoncées en conception ; un texte de cours seul ne constitue pas un brouillon fonctionnel. Configurer ou faire configurer notes, achèvement et restrictions nécessaires à son essai, dans le périmètre autorisé. Examiner d’abord les vidéos existantes, y compris en ligne, et fournir au moins une capture annotée pour chaque manipulation d’interface ; une intégration ou URL peut convenir sans nouveau média. Vérifier droits et accès, signaler au responsable les limites du constructeur. Pour une vidéo à produire, préparer le scénario ou découpage. Les cas d’exercice sont réalistes ; aucune mention de chantier ni bandeau « fictif » dans le contenu apprenant.

Faire importer les livrables par l’utilisateur dans un cours de test autorisé de son Moodle existant ; guider les manipulations complémentaires. Faire parcourir le brouillon pour valider le fond et le fonctionnement, d’abord sur le pilote puis sur les autres sections. Recueillir commentaires et captures utiles aux maquettes ; un retour libre suffit. Conserver les sources modifiables et une présentation simple, lisible et accessible ; la finition des médias et du graphisme vient après ce retour. Signaler au responsable les éléments provisoires et limites de fabrication, hors des vues apprenant.

**Contrôle UX :** KISS maintenu dans le brouillon ; choix d’activités cohérents ; titres d’action sans codes ; notes au responsable séparées ; consignes et rétroactions propres à chaque étape. Exemple : « Déposez votre capture » ; contre-exemple : « Réalisez cette étape » répété partout.

**À valider :** exactitude, ton, charge et fonctionnement des activités préparées, d’abord sur la section pilote puis sur le reste du cours ; commentaires et captures nécessaires à la passe UX. Sans import ou manipulation réalisée, annoncer ce qui reste à essayer avant ce passage.

## 3. Maquettes UX

Partir du contenu et du fonctionnement validés au brouillon, des captures du site cible et des besoins des apprenants : hiérarchie visuelle, repérage, lisibilité, action principale, aide, accessibilité et usage mobile. Inclure les documents PDF/Word et l’attestation dans cette passe ; reprendre les références approuvées. Distinguer amélioration éditoriale, comportement natif et fonction non vérifiée avant de proposer une correction. Bootstrap et le thème sont des moyens techniques ; leur apparence par défaut ne définit pas la direction graphique.

Pour une nouvelle direction, présenter **deux ou trois propositions sur la même section pilote**, avec le contenu brouillon validé. Si une direction de référence est déjà approuvée, la reprendre par défaut et présenter seulement les adaptations nécessaires. Après le choix, essayer son HTML dans le thème et l'éditeur cibles si l'accès et l'autorisation existent, avant la déclinaison.

Produire une **maquette HTML complète par section**, réutilisable à la finalisation lorsque sa compatibilité est établie. Montrer sur écran et mobile le vrai texte du brouillon, les médias provisoires et les états utiles. Une forme allégée pour des sections répétitives exige l'accord de la personne responsable ; un gabarit commun ne remplace pas automatiquement les vues de chaque section.

Pour chaque activité requise, préciser ce que l'apprenant fait, ce qui déclenche la coche et la rétroaction reçue. Avant l'activité, il doit comprendre comment obtenir l'achèvement ; après, il doit pouvoir constater son état. Montrer aussi attente de correction/traitement et accès restreint lorsqu'ils existent. Distinguer **états illustrés** et **comportements vérifiés dans Moodle** : dessiner une coche ne prouve pas son déclenchement.

L'accessibilité est travaillée dès cette phase : titres, contraste, clavier, textes alternatifs et petit écran. Une image peut explorer une direction mais ne démontre pas la faisabilité Moodle. Sans accès au site, consigner pour le responsable la réserve technique à lever avant finalisation de l’intégration, hors du contenu apprenant. Si une contrainte modifie une maquette approuvée, présenter l'adaptation et son effet avant de l'appliquer.

Partir de **captures du rendu réel** : captures fournies dans le site cible par la personne responsable, ou captures automatiques dans un Moodle local si l’environnement le permet. Ces dernières peuvent être bloquées et le thème local peut différer ; ne pas contourner une restriction. Les captures du site cible restent la validation finale du rendu. Sans capture accessible, préparer le HTML et consigner la réserve dans le projet, sans prétendre avoir vu le résultat.

**Contrôle UX :** vues écran/mobile simples ; activités utiles ; titres lisibles sans doublons ; aucune note de chantier dans les vues apprenant ; texte spécifique, aucun composant vide. Exemple : capture du pilote réellement rendu ; contre-exemple : maquette seule présentée comme preuve Moodle.

**À valider :** direction choisie, maquettes de chaque section, adaptations et limites. Le test de présentation ne remplace pas l'essai fonctionnel de phase 5. Voir [qualite-validation.md](qualite-validation.md).

## 4. Finalisation

Appliquer les maquettes approuvées aux activités et ressources du brouillon, y compris documents et attestation. Finaliser les médias et sous-titres retenus ; réutiliser le HTML compatible et les objets déjà préparés, sans reconstruction sans raison. Compléter les manipulations manuelles annoncées avec les moyens de [capacites.md](capacites.md) ; une procédure documentée n'implique pas un générateur livré. Tout changement significatif du contenu, d’outil ou de direction revient à validation.

Vérifier séparément notes, passage, achèvement, accès et dépendances déjà préparés au brouillon. Conserver les sources et préparer la sauvegarde/livraison de validation. Présenter tout changement affectant un choix déjà approuvé.

**Contrôle UX :** relecture du parcours complet selon [Concevoir une section](concevoir-section.md) : KISS, véhicules adaptés, titres sans codes, deux publics séparés, absence de remplissage répété et de composants vides. Exemple : consigne et pièces dans le Devoir ; contre-exemple : lien vers un média absent. Le futur contrôle automatique ne remplace pas cette relecture et n’est pas encore livré.

**À valider :** cours complet et fichiers préparés, écarts résolus ou explicités, préparation de l'essai. Aucun déploiement n'est déduit de cette validation.

## 5. Essai

Le parcours normal consiste à faire importer/restaurer les livrables par l'utilisateur dans un cours de test autorisé de son Moodle existant, puis à recueillir les résultats de la fiche d'essai et à corriger. Ne pas demander d'installation de serveur local ; voir [le parcours d'import](sauvegardes.md#parcours-utilisateur-sans-serveur-local).

Dans un cours de test autorisé avec accès apprenant prévu, restaurer si pertinent et essayer **tout le parcours**, pas seulement la section pilote : réussite et échec avec rôle apprenant, fichiers/liens, notes, achèvement, restrictions, attestation et rétroaction, clavier et mobile. Ajouter l'état d'attente lorsqu'une correction humaine intervient.

Comparer les résultats aux critères du plan ; corriger et reprendre les contrôles touchés. Si l'environnement manque, la phase reste incomplète et ses fonctions non testées sont annoncées ; aucune réussite n'est supposée à partir du HTML ou du XML.

Pour le développement de la skill, une visite automatisée dans une instance locale déjà disponible et autorisée reste facultative ; elle ne justifie pas d'en installer une chez l'utilisateur. Utiliser un compte apprenant de test, des vues écran et téléphone et un parcours des sections/activités. Examiner accueil, repérage, dépliants et actions, état de la coche et affichage du nom du cours. Ne pas inclure de paramètres de session dans les traces. Si les outils manquent, consigner les limites sans contourner les restrictions. Les observations et captures du responsable dans le site cible restent la validation finale ; toute visite automatisée d'un site réel exige son autorisation explicite.

**Contrôle UX :** sous rôle apprenant, compter les changements de page utiles, vérifier adéquation des activités et repérage par les titres, absence de notes au responsable et de phrases génériques. Exemple : une trace remise donne l’état configuré ; contre-exemple : une Page cochée censée prouver une remise. Conserver les limites d’essai dans le projet.

**À valider :** résultats observés, corrections, limites restantes et décision de préparation à la production.

## Mise en production

Présenter la cible, l'opération, les effets et le retour prévu. Obtenir l'autorisation explicite de la personne responsable pour cette mise en production. Privilégier un nouveau cours pour restaurer ; sauvegarder le cours existant avant restauration ou mise à jour et adapter le retour au risque.

Pour un cours avec participants, analyser les effets sur contenus, tentatives, notes et achèvements. Si la restauration supprime le contenu existant, l'autorisation doit nommer cette option ; la sauvegarde préalable doit inclure les données des participants nécessaires au retour, conservées dans un emplacement autorisé. Ne pas procéder sans droits, couverture de sauvegarde et protection appropriés. Voir la règle détaillée dans [sauvegardes.md](sauvegardes.md).

Après l'opération autorisée, vérifier les fonctions essentielles dans la destination et fournir un bilan. **Contrôle UX :** confirmer le repérage, les liens, le parcours et les états réellement visibles ; comparer aux captures approuvées, sans introduire de notes de chantier. Une instruction de préparation de fichiers n'autorise pas cette phase.

## Maintenance

**Contrôle UX :** examiner les retours d’usage, préserver les choix approuvés et vérifier que la modification n’ajoute ni navigation inutile ni contenu générique ; faire valider les adaptations qui changent le parcours.

Examiner les rétroactions et les changements de logiciel, de politique ou de sources pertinents au cours. Garder dans le projet les versions, modifications et vérifications. Reprendre les validations touchées selon la portée ; les fusions de phases restent une décision humaine.

Avant une mise à jour H5P d'une activité avec tentatives, préserver l'état et vérifier les effets sur les résultats. Les clés d'interaction permettent désormais des `subContentId` stables hors ligne, sans garantie établie de continuité. Ajouter des clés à une ancienne fiche ne conserve pas ses anciens UUID aléatoires. Distinguer nouvelle activité, mise à jour et déplacement d'interactions ; voir [chaine-video-h5p.md](chaine-video-h5p.md).

**Portée :** procédure documentaire ; son intégration ne prouve ni son efficacité en usage réel ni l'exécution des phases dans une instance.
