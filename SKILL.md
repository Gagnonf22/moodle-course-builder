---
name: moodle-course-builder
description: Créer un cours Moodle, le concevoir, le réviser ou examiner une sauvegarde .mbz. Utiliser pour préparer le parcours et les maquettes, une vidéo interactive H5P, un test, un devoir, une attestation ou la rétroaction ; choisir les activités, configurer le suivi et vérifier une restauration. Fournit des procédures et des outils dont la portée de fabrication est précisée par capacité.
---

# Construire des cours Moodle

Transformer le besoin en un cours modifiable et vérifiable. Adapter la forme aux objectifs et au public : une vidéo interactive, un devoir, un Livre et un test natif répondent à des besoins différents.

Pour créer un cours, appliquer la [démarche de cocréation](references/conception-cours.md) et le [modèle de base](references/modele-cours-de-base.md) : socle commun, activités de sections adaptées aux objectifs. La personne responsable valide chaque phase ; le plan justifie les choix et écarts au socle et distingue fabrication par la skill et création manuelle dans Moodle. Une petite modification reprend seulement les phases pertinentes. Concevoir l'UX et le visuel avant de choisir leur réalisation dans le thème.

## Commencer

Reprendre le plan, les décisions et les sources déjà présents dans le projet. Identifier la demande : concevoir, fabriquer un contenu, intervenir dans Moodle, examiner une sauvegarde ou corriger un problème. Ne charger que la référence utile ci-dessous.

Pour une intervention dans Moodle, relever version, rôle, format, thème et composants nécessaires à cette intervention. Pour un travail hors ligne, consigner les inconnues qui affecteront l'import ; ne pas exiger un accès au site pour rédiger un plan ou fabriquer un média.

Choisir la voie réellement disponible : interface Moodle, service autorisé, script local de validation ou retouche de copie. La présence d'un composant dans une sauvegarde ne prouve pas qu'un outil peut le créer sur le site cible.

## Trouver la bonne procédure

| Besoin | Lire seulement ce qui s'applique |
|---|---|
| Concevoir un cours, choisir sa structure et ses activités | [conception-cours.md](references/conception-cours.md) |
| Savoir ce qui est déjà automatisé et choisir la voie de réalisation | [capacites.md](references/capacites.md) |
| Créer sections, Pages, Livres, fichiers ou navigation | [structure-ressources.md](references/structure-ressources.md) |
| Encoder une vidéo, préparer un VTT, construire Interactive Video ou Question Set | [chaine-video-h5p.md](references/chaine-video-h5p.md) |
| Intégrer un H5P dans une section et conserver une activité de suivi | [h5p-integration.md](references/h5p-integration.md) |
| Créer un test Moodle et sa banque, choisir ou reprendre des types de questions | [tests-questions.md](references/tests-questions.md) |
| Construire un devoir, une remise, une grille ou un guide de correction | [devoirs-correction.md](references/devoirs-correction.md) |
| Recueillir une rétroaction : Feedback ou Questionnaire | [retroaction.md](references/retroaction.md) |
| Forum, glossaire, leçon, jeu ou autre activité spécialisée | [activites-specialisees.md](references/activites-specialisees.md) |
| Notes, achèvement, restrictions, badges ou attestation | [suivi-reconnaissance.md](references/suivi-reconnaissance.md) |
| Examiner, modifier, sauvegarder ou restaurer un .mbz | [sauvegardes.md](references/sauvegardes.md) ; [retouches H5P/attestation](references/retouches-activites.md) ; socle technique : [mbz-retouches-locales.md](references/mbz-retouches-locales.md) |
| Choisir une API, un connecteur ou un script privilégié | [automatisation.md](references/automatisation.md) ; [contrat de vérification](references/contrat-structure.md) |
| Mettre en forme, vérifier l'accessibilité et essayer le cours | [qualite-validation.md](references/qualite-validation.md) |

## Contraintes qui changent la réalisation

- Préserver les sources. Identifier les objets par des clés de projet stables ; relever ou remapper leurs identifiants Moodle, sans recopier ceux d'un autre cours.
- Distinguer paquet H5P, banque de contenus, activité source, affichage intégré, tentative, note et achèvement. Vérifier les liens nécessaires au besoin réel.
- Ne jamais simplifier silencieusement une question, sa notation ou les dépendances d'une activité pour la rendre exportable.
- Conserver contenus de cours, identifiants, données de participants et secrets dans le projet autorisé. Les exemples livrés ici sont synthétiques.
- L'autorisation de préparer des fichiers ne vaut pas autorisation d'installer, d'envoyer ou de publier. Les scripts PHP inclus restent réservés à une validation locale ; voir leurs limites avant usage.

## Livrer

Présenter les fichiers utiles, les opérations réellement faites, les vérifications et les limites restantes. Employer les statuts de [capacites.md](references/capacites.md) : une observation de sauvegarde, un test hors ligne et un essai étudiant ne couvrent pas la même chose. Ne pas transformer une réussite sur un cours en garantie générale. Pour une vérification de provenance ou un ajout de capacité, consulter [sources-portee.md](references/sources-portee.md).
