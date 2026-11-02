# Exemple de plan — Réaliser et vérifier une tâche numérique

Document du **responsable**, à adapter et valider en phase 1 ; ni contrat PHP ni cours créé. Les données d'exercice sont inventées ; cette note de préparation ne va pas dans le cours. Appliquer le [socle](../references/modele-cours-de-base.md) et [Concevoir une section](../references/concevoir-section.md).

Public débutant ; objectif : réaliser une manipulation, constater son effet et expliquer un contrôle. Durée indicative 30 à 45 minutes à réviser après essai. Projet distinct avec sources, DECISIONS.md, ROADMAP.md. Direction et attestation approuvées reprises par défaut.

Parcours visible : **Bien démarrer** (section 0 de présentation), **Repérer le bon résultat** (pilote, démonstration et entraînement), **Réaliser et vérifier** (pratique), **Vérifier ses acquis** (test final, attestation, avis). Les sections partagent une structure de repérage et des indices propres au contenu.

## Tableau obligatoire par activité ou ressource

Chaque ligne identifie un élément dans la première colonne. Une section ou un média intégré n'est pas un module Moodle supplémentaire : son champ ou son support est précisé. Banque technique et pièces jointes ne sont pas des activités à afficher séparément.

| Type Moodle exact (élément identifié) | Pourquoi cet outil : objectif et règle de choix | Alternative écartée et raison | Condition d'achèvement | Fabriqué par la skill ou à créer à la main |
|---|---|---|---|---|
| Section 0, `course_sections.summary` — Bien démarrer | Présenter bandeau, objectifs, déroulement, durée et conditions de l'attestation | Premier module direct : aucune vue du parcours | Aucun achèvement propre au résumé ; préparation expliquée | HTML préparé par l'IA ; intégration et contrôle du résumé riche à confirmer techniquement ou à faire dans l'éditeur |
| Section de travail, `course_sections.summary` — Repérer le bon résultat | Étapes et points clés sur place ; pilote | Page courte séparée : changement d'écran inutile | Aucun achèvement propre au résumé | HTML préparé ; éditeur manuel ou contrat à confirmer |
| Vidéo en ligne intégrée au résumé — Observer la commande | Réutiliser une démonstration adaptée, sans nouveau média | Nouvelle vidéo produite sans nécessité : travail sans apport | Consultation libre, aucun score | Création manuelle dans l'éditeur ; vérifier droits, accès et sous-titres. Le script H5P exige un média local |
| Image intégrée au résumé — Repérer le résultat | Au moins une capture annotée par manipulation, action aussi décrite en texte | Consigne textuelle seule pour débutant ne connaissant pas l'interface | Aucun achèvement propre à l'image | Capture et annotation à produire dans l'environnement autorisé ; intégration manuelle si nécessaire |
| `h5pactivity` — Anticiper l'effet, affiché dans la section | Entraînement sans conséquence, retour immédiat | Test natif pour chaque exercice : enjeu et navigation superflus | Pas de seuil ni d'achèvement requis pour cet entraînement | Paquet IV/QS fabriqué si entrées adaptées ; source puis retouche d'intégration fournie selon profil. Défaut automatique à compléter/éprouver |
| `quiz` — Décider avant une modification sensible | **Écart proposé au seul test final :** jalon formatif avant une opération à conséquences, retour ciblé ; charge courte à confirmer | H5P sans enjeu seul : pas de vérification mesurée de cette décision importante | Réussite au seuil justifié dans le projet | Profil v3 fabriqué pour les types couverts ; banque, questions et réglages à vérifier. Test supplémentaire à valider explicitement |
| Section de travail, `course_sections.summary` — Réaliser et vérifier | Consignes visibles, résultat attendu et règle de la coche avant l'activité | Livre de quelques paragraphes : sous-navigation | Aucun achèvement propre au résumé | HTML préparé ; intégration et vérification riches à confirmer |
| `assign` — Remettre le résultat | Pratique avec capture et explication, sans charge de correction obligatoire | Page cochée : aucune trace remise | À la remise finalisée, sans attendre une note | Profil noté livré ; pratique sans correction et pièces de consigne à compléter/éprouver, sinon configuration manuelle |
| Fichier supplémentaire de la consigne `assign` — Fichier de départ | Donner le matériau au même endroit que l'exercice | Ressource `resource` séparée : un clic et un élément de plus | Aucun achèvement séparé | Ajout manuel au Devoir tant que le complément n'est pas éprouvé ; aucun module Fichier distinct |
| Section finale, `course_sections.summary` — Vérifier ses acquis | Expliquer seuil, reprises et accès à l'attestation | Pages de consignes séparées : dispersion | Aucun achèvement propre au résumé | HTML préparé ; voie d'intégration à confirmer |
| `qbank` — Banque de l'évaluation, masquée | Conserver les questions à l'endroit attendu par Moodle 5.1 | Questions sans contexte de banque correct : références fragiles | Aucun ; objet technique non affiché | Fabriqué par le profil v3, références après restauration à vérifier |
| `quiz` — Vérifier ses acquis | Évaluation finale par mini-scénarios de transfert ; seuil proposé 70 % à justifier/valider | Question Set d'entraînement transformé en épreuve par facilité de script | Réussite au seuil et reprises décidées | Fabriqué v3 pour les types couverts. Questions sans réponse courte hors orthographe ; tentatives illimitées à traiter séparément dans U2 |
| `customcert` — Télécharger l'attestation | Reconnaître la réussite avec le modèle approuvé | Certificat simplifié nouveau : écart visuel non autorisé | Accès après réussite du test final ; consulter selon le plan | Native v4 si le modèle est conservé, sinon retouche depuis modèle couvert ou voie manuelle validée. Plusieurs conditions attendent U2 |
| `feedback` — Donner son avis | Retour sur la formation, sans note | `questionnaire` si ses fonctions ne sont pas nécessaires ici | À l'envoi, selon configuration éprouvée ; ne conditionne pas l'attestation dans cet exemple | Fabriqué v4 ; décider identification/anonymat et vérifier sous rôle apprenant |

Un lexique supplémentaire demanderait sa propre ligne `glossary` ; création manuelle tant que le nouveau profil n'est pas éprouvé. Aucun Livre ni Leçon nécessaire ici. Le jalon formatif est une **proposition motivée**, pas une approbation acquise ; le retirer si l'objectif et son risque ne le justifient pas.

**La construction attend la validation de ce tableau. Tout changement d'outil ultérieur revient au responsable avant exécution**, avec mise à jour de la ligne et de ses effets. Une limite du script ne vaut pas autorisation de substitution.

Socle prévu : accueil, coche expliquée, évaluation finale avec seuil, attestation et rétroaction. La pratique complète le test. Modifier ce socle ou ajouter un test demande une décision explicite. Exemple de consigne apprenant : « Téléchargez le fichier joint, réalisez l'opération et remettez la capture et votre explication ; la remise finalisée déclenche la coche ». Vérifier ce comportement. Contre-exemple : « M02 — Atelier fictif : cochez la Page ».

## Validations suivantes

Phase 2 : rédiger le pilote puis les autres sections. Phase 3 : reprendre la direction approuvée, maquette par section écran/mobile avec captures réelles et réserves pour le responsable. Phase 4 : cours final sans média absent, composant vide ou code interne. Phase 4b : parcours apprenant, remise, états échec/réussite, PDF et navigation ; proposer une visite automatisée locale si disponible. Captures du site cible pour la validation finale du rendu. Toute visite d'un site réel et la mise en production demandent leur autorisation explicite.

Consigner date, phase, éléments et réserves dans le projet. Une forme légère de maquette ou une fusion de phases exige décision humaine. Aucun état dessiné n'est une preuve d'achèvement.
