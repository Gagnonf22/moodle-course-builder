---
name: concepteur-cours-moodle-desuet
description: Créer un cours Moodle, le concevoir, le réviser ou examiner une sauvegarde .mbz. Utiliser pour préparer le parcours et les maquettes, une vidéo interactive H5P, un test, un devoir, une attestation ou la rétroaction ; choisir les activités, configurer le suivi et vérifier une restauration. Fournit des procédures et des outils dont la portée de fabrication est précisée par capacité.
---

# Construire des cours Moodle

Transformer le besoin en un cours modifiable et vérifiable. Adapter la forme aux objectifs et au public : une vidéo interactive, un devoir, un Livre et un test natif répondent à des besoins différents.

Pour créer un cours, appliquer la [démarche de cocréation](references/conception-cours.md) et le [modèle de base](references/modele-cours-de-base.md) : socle commun, activités de sections adaptées aux objectifs. La personne responsable valide chaque phase ; le plan justifie les choix et écarts au socle et distingue fabrication par la skill et création manuelle dans Moodle. Une petite modification ou un essai de composants reprend seulement les phases pertinentes ; ne pas le juger comme un cours achevé. Reprendre par défaut la direction et l’attestation du cours de référence approuvé.

**Cinq passes :** 1. Conception → 2. Brouillon fonctionnel, importé et commenté dans le Moodle existant → 3. Maquettes UX à partir du contenu validé et des captures → 4. Finalisation → 5. Essai. La mise en production est une opération distincte, autorisée pour sa cible. À chaque passage, annoncer **ce qui est prêt, ce qui reste provisoire, la validation attendue et la suite** ; attendre cette validation avant la passe suivante. La finition visuelle vient après le brouillon utilisable, en conservant lisibilité et accessibilité de base dès le départ.

La construction attend la validation du tableau obligatoire de phase 1, une ligne par activité ou ressource. Tout changement d’outil ultérieur revient à la personne responsable avant exécution ; voir [la démarche](references/conception-cours.md).

## Commencer

**Usage sans serveur local :** ne pas demander à l'utilisateur d'installer, de démarrer ou de transporter un serveur Moodle pour utiliser la skill. Préparer hors ligne les livrables réellement réalisables, puis lui faire importer/restaurer le cours dans son Moodle existant, dans un cours de test autorisé. Fournir les étapes d'import, les manipulations complémentaires et une fiche d'essai ; recueillir ses observations et corriger. Les scripts PHP locaux sont des outils facultatifs de développement et de validation de la skill, pas des prérequis utilisateur. Sans voie de fabrication disponible pour une fonction, annoncer la limite et fournir les ressources et opérations manuelles nécessaires, sans promettre un `.mbz` autonome. Voir [le parcours d'import](references/sauvegardes.md#parcours-utilisateur-sans-serveur-local).

Créer ou reprendre un dossier de projet propre au cours, distinct de la skill : sources, `DECISIONS.md` et `ROADMAP.md`. Réutiliser son organisation existante. Reprendre le plan, les décisions et les sources déjà présents dans le projet. Identifier la demande : concevoir, fabriquer un contenu, intervenir dans Moodle, examiner une sauvegarde ou corriger un problème. Ne charger que la référence utile ci-dessous.

Pour une intervention dans Moodle, relever version, rôle, format, thème et composants nécessaires à cette intervention. Pour un travail hors ligne, consigner les inconnues qui affecteront l'import ; ne pas exiger un accès au site pour rédiger un plan ou fabriquer un média.

Choisir la voie réellement disponible : préparation de fichiers, retouche de copie, puis import par l'utilisateur ; interface ou service existant uniquement si l'intervention est autorisée. Réserver les scripts locaux au développement dans un environnement déjà disponible et autorisé. La présence d'un composant dans une sauvegarde ne prouve pas qu'un outil peut le créer sur le site cible.

## Trouver la bonne procédure

| Besoin | Lire seulement ce qui s'applique |
|---|---|
| Concevoir un cours, choisir sa structure et ses activités | [conception-cours.md](references/conception-cours.md) ; [outil de choix](references/modele-cours-de-base.md#choisir-les-activités) |
| Organiser une section, ses titres, médias et actions selon KISS | [concevoir-section.md](references/concevoir-section.md) |
| Savoir ce qui est déjà automatisé et choisir la voie de réalisation | [capacites.md](references/capacites.md) |
| Créer sections, Pages, Livres, fichiers ou navigation | [structure-ressources.md](references/structure-ressources.md) |
| Encoder une vidéo, préparer un VTT, construire Interactive Video ou Question Set | [chaine-video-h5p.md](references/chaine-video-h5p.md) |
| Intégrer un H5P dans une section et conserver une activité de suivi | [h5p-integration.md](references/h5p-integration.md) |
| Créer un test Moodle et sa banque, choisir ou reprendre des types de questions | [tests-questions.md](references/tests-questions.md) |
| Construire un devoir, une remise, une grille ou un guide de correction | [devoirs-correction.md](references/devoirs-correction.md) |
| Recueillir une rétroaction : Feedback ou Questionnaire | [retroaction.md](references/retroaction.md) |
| Forum, glossaire, leçon, jeu ou autre activité spécialisée | [activites-specialisees.md](references/activites-specialisees.md) |
| Notes, achèvement, restrictions, badges ou attestation | [suivi-reconnaissance.md](references/suivi-reconnaissance.md) |
| Salutation par prénom et barre de progression | [personnalisation-progression.md](references/personnalisation-progression.md) ; prévoir les replis sans composant RÉCIT |
| Examiner, modifier, sauvegarder ou restaurer un .mbz | [sauvegardes.md](references/sauvegardes.md) ; [retouches H5P/attestation](references/retouches-activites.md) ; socle technique : [mbz-retouches-locales.md](references/mbz-retouches-locales.md) |
| Choisir une API, un connecteur ou un script privilégié | [automatisation.md](references/automatisation.md) ; [contrat de vérification](references/contrat-structure.md) ; [contrat v5](references/contrat-experience-v5.md) pour ressources et progression |
| Mettre en forme, essayer le cours ou diagnostiquer un dysfonctionnement | [qualite-validation.md](references/qualite-validation.md) ; [boutons H5P vides après import](references/retouches-activites.md#boutons-h5p-vides-après-import) |

## Contraintes qui changent la réalisation

- Préserver les sources. Identifier les objets par des clés de projet stables ; relever ou remapper leurs identifiants Moodle, sans recopier ceux d'un autre cours.
- Distinguer paquet H5P, banque de contenus, activité source, affichage intégré, tentative, note et achèvement. Vérifier les liens nécessaires au besoin réel.
- Ne jamais simplifier silencieusement une question, sa notation ou les dépendances d'une activité pour la rendre exportable.
- Séparer les deux publics : cours utilisable pour l’apprenant, choix/statuts/réserves dans les fichiers du responsable. Les données d’exercice peuvent être inventées sans étiqueter le produit « fictif ». Conserver données et secrets uniquement dans les emplacements autorisés ; les exemples de la skill restent synthétiques.
- L'autorisation de préparer des fichiers ne vaut pas autorisation d'installer, d'envoyer ou de publier. Les scripts PHP inclus restent réservés à une validation locale ; voir leurs limites avant usage.

## Livrer

Présenter les fichiers utiles, les opérations réellement faites, les vérifications et les limites restantes. Employer les statuts de [capacites.md](references/capacites.md) : une observation de sauvegarde, un test hors ligne et un essai étudiant ne couvrent pas la même chose. Ne pas transformer une réussite sur un cours en garantie générale. Pour une vérification de provenance ou un ajout de capacité, consulter [sources-portee.md](references/sources-portee.md).
