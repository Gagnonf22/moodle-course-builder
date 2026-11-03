# Historique

## Non publié — 2026-11-03 — U2, ressources et progression

- Contrat v5 rétrocompatible : Glossaire, fichiers de consigne du Devoir, pratique sans note, H5P d'entraînement intégré par défaut et comparaison du HTML complet des sections.
- Tests : tentatives illimitées explicites et achèvement à une tentative terminée, distinct de la réussite. Attestation avec conditions conjointes d'achèvement et de note, remappées après restauration.
- Glossaire : les définitions du modèle sont transportées sans données utilisateurs dans une zone native de fichiers ; étape CLI locale explicite après restauration, car la restauration native users=0 omet les entrées. Aucun changement du cœur Moodle ni inclusion d'utilisateurs.
- Vérifications par doublures et essais réels locaux ; portée, prérequis et limites dans les capacités et le contrat v5. Aucun push ni publication.

## Non publié — 2026-11-02 — Correction U1 et nom français

- Nouveau nom `concepteur-cours-moodle` (ancien nom : `moodle-course-builder`) et inspecteur `inspecter_mbz.py`, avec test et appels alignés ; messages de l’inspecteur en français. Aucun changement de capacité ; espace UUID historique conservé à valeur identique.
- Tableau obligatoire à cinq colonnes, validation avant construction et changement d’outil soumis au responsable ; exemple par activité/ressource. Accueil, captures, repères de section et noms de cours renforcés.
- Tests natifs aux jalons justifiés et visite automatisée locale proposée en phase 4b. Exclusion de la navigation des répétitions, contrôle séparé des titres prévu pour U3.

## Non publié — 2026-11-02 — U1, conception de l'expérience

- Description de section comme page principale, KISS, titres d'action, contenu propre à chaque étape et absence de composants vides.
- Outil de choix : H5P intégré pour l'entraînement, test natif pour évaluer, Devoir avec trace pour pratiquer, Glossaire pour le lexique ; Page/Livre limités aux besoins de lecture, Leçon à éviter.
- Expérience contrôlée aux phases 1 à 4b, séparation des deux publics, direction visuelle et attestation de référence reprises par défaut ; règles de questions et relecture des distracteurs.
- Dossier de projet distinct, vidéos en ligne et captures annotées, maquettes depuis captures réelles ; convention des liens distinguée des exigences WCAG 2.2.
- Exemple de plan aligné sur les capacités réellement livrées et les compléments encore à éprouver. Documentation seulement : aucun script, contrat, test ou générateur modifié ; aucune publication.

## 0.7.0 — 2026-11-01

- Refonte en français : entrée courte et aiguillage vers les références utiles, matrice tâche/prérequis/preuve/limites et exemples synthétiques.
- Démarche de cocréation : conception, brouillon, maquettes, finalisation, essai 4b, production autorisée et maintenance ; validation humaine à chaque phase. Section pilote, directions visuelles, maquette par section, accessibilité et critère d'achèvement explicite.
- Socle par défaut : accueil, achèvement expliqué, évaluation finale avec seuil, attestation après réussite et rétroaction. Activités des sections adaptées aux objectifs et moyens réellement disponibles.
- Chaîne vidéo/VTT/H5P : encodage et affiches, corrections de sous-titres, Interactive Video et Question Set, clés d'interaction pour UUID stables, langue et libellé de piste configurables. Huit paquets reconstruits et comparés indépendamment ; continuité des tentatives après mise à jour non démontrée.
- Retouches génériques de copies .mbz : lecture des identifiants existants, intégration d'activités H5P dans les sections, ajout d'une attestation depuis un modèle couvert, fond et images PNG remappés, sorties nouvelles et refus des ambiguïtés/doubles applications. Déclaration XML et contexte des images corrigés après essai réel.
- Scripts PHP de construction, sauvegarde et vérification réservés à une instance locale isolée. Sauvegarde sans utilisateurs avec inclusion contrôlée des fichiers et de la banque de contenus. Contrats de structure v1 à v4 rétrocompatibles.
- Construction native : Livre et chapitres ; Devoir individuel texte/fichier/mixte avec grille ou guide ; banque qbank et test à choix unique/multiple, vrai/faux, réponse courte et numérique avec tolérance ; Feedback ; Leçon non notée à branchements ; attestation simple créée directement.
- Essais réels dans Moodle 5.1.8+ local et Custom certificate 5.0.11 : construction, sauvegarde, restauration, remises/correction, tentatives échec/réussite, achèvements, formulaires, une branche de Leçon, restriction d'attestation et PDF avec fond. Contrôles indépendants après chaque étape ; 114 tests hors ligne. Preuves et réserves détaillées dans la matrice des capacités.
- Distribution autonome : README français, licence MIT, exemples fictifs ; exclusion des cours sources, médias, validations et archives de développement. Installation par copie du dossier complet.

## 0.1 à 0.6.9 — Versions antérieures

Premières versions d'exploration, références Moodle/H5P, analyses et inspection de sauvegardes, traçabilité des sources et garde-fous. La refonte reprend et réécrit les connaissances utiles ; les capacités de génération et les essais d'instance ci-dessus appartiennent à la version 0.7.0. Les archives historiques restent séparées de cette distribution.
