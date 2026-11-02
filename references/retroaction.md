# Recueillir la rétroaction : Feedback ou Questionnaire

Lire pour une enquête, un bilan ou un débreffage. Les composants `feedback` et `questionnaire` sont distincts ; le mot « questionnaire » employé dans une demande ne suffit pas à choisir entre eux et un test noté.

## Choisir

| Intention | Choix à examiner |
|---|---|
| Recueillir une appréciation ou un bilan simple, sans note | Feedback, si disponible |
| Employer des fonctions propres au plugin Questionnaire | Questionnaire, après vérification de son installation et de ses réglages |
| Évaluer des réponses avec score | Test Moodle ou H5P selon le suivi et les types requis |
| Faire commenter une production par le correcteur | Retour du Devoir, plutôt qu'enquête supplémentaire |

Déterminer avant la création : finalité, destinataires des résultats, identification ou anonymat, champs obligatoires, fréquence de réponse, période d'accès et condition d'achèvement souhaitée. Ne pas promettre l'anonymat technique ou organisationnel sur la seule foi d'un titre de formulaire.

## Construire un Feedback

Ajouter l'activité, régler l'identification/anonymat et les autres options nécessaires, puis créer et ordonner les éléments. Distinguer choix, textes de réponse et éléments informatifs ; tester les obligations et la page de fin. Les options de réponses multiples et de consultation des résultats doivent correspondre au besoin. [Réglages Feedback](https://docs.moodle.org/501/en/Feedback_settings).

Le constructeur local propose un [profil Feedback v4](contrat-parcours-v4.md) : choix unique, texte court/long, information et texte informatif, anonymat explicite, une réponse et achèvement sur envoi. Ne pas l'utiliser pour une enquête dont les fonctions dépassent ce profil sans annoncer la limite.

**Constat Moodle 5.1.8+ local, 2026-11-01 :** en mode anonyme natif, `anonymous_response=1` mais un userid reste dans la table de réponse. Ce mode ne prouve donc pas l'absence d'association technique en base. Ne pas exporter ces données comme anonymisées sur la seule foi du réglage ; appliquer les accès et règles de traitement du projet.

Exemple synthétique adaptable : utilité perçue (échelle à définir), difficulté rencontrée (choix), application envisagée (texte facultatif). Ne pas reprendre un formulaire complet sans justifier chaque champ. Une activité créée sans ses éléments n'est pas une enquête livrée.

## Construire un Questionnaire

Vérifier le composant et la version, créer l'activité puis ses questions et choix. Configurer le mode de réponse et les fonctions spécifiques seulement si elles sont nécessaires et présentes. Un schéma d'export Feedback n'est pas un schéma Questionnaire ; aucune substitution XML directe n'est proposée. [Module Questionnaire](https://docs.moodle.org/501/en/Questionnaire_module).

## Vérifier

Envoyer une réponse fictive avec le rôle prévu ; essayer une omission d'un champ obligatoire et la répétition de réponse lorsque la fréquence importe. Contrôler les résultats visibles pour l'apprenant et le responsable, puis l'achèvement si configuré. Vérifier l'affichage de l'information sur l'usage des réponses et l'absence de données personnelles non nécessaires.

**Portée :** Feedback éprouvé dans Moodle 5.1.8+ local le 2026-11-01 : construction, sauvegarde/restauration des éléments et réglages ; formulaire incomplet refusé sans réponse complète enregistrée ; envois complets nominatif/anonyme acceptés, commentaire facultatif omis, achèvement constaté ; seconde réponse refusée. Le plugin Questionnaire reste sans générateur et testé par doublure seulement dans le vérificateur. Le rendu des rapports de résultats et les autres versions restent à essayer sur le site cible.
