# Modèle de cours par défaut

Utiliser en phase 1 de la [démarche de cocréation](conception-cours.md). Le plan confirme le socle ou justifie chaque écart pour validation humaine. KISS : un seul endroit pour agir, peu de clics et de changements de page, sans ajouter de sous-niveaux de navigation. Lire [Concevoir une section](concevoir-section.md) pour la réalisation éditoriale.

## Socle par défaut

| Élément | À préciser et vérifier |
|---|---|
| Accueil | Section 0 avec bandeau, objectifs d’ensemble, déroulement, durée, conditions d’attestation, préparation, aide et suivi |
| Achèvement expliqué avant chaque activité requise | Action, déclencheur de la coche, retour, attente éventuelle ; état constatable après l'action |
| Évaluation finale avec seuil | Test natif autocorrigé par défaut ; seuil justifié, tentatives, relecture et règle de passage explicites |
| Attestation après réussite | Reprendre le modèle de référence approuvé ; vérifier plugin, restrictions et PDF |
| Rétroaction sur la formation | Feedback ou Questionnaire selon besoin et composants ; identification/anonymat, obligations et visibilité à décider |

Décider si la rétroaction conditionne l'attestation. Un Devoir peut compléter l'évaluation d'une compétence pratique ; un remplacement du test final se justifie et se valide, sans convertir l'entraînement H5P en épreuve par facilité de fabrication. Un score H5P ne configure ni passage Moodle ni émission d'un PDF.

**Exemple :** accueil, pratique avec trace, test final avec seuil motivé, attestation et Feedback. **Contre-exemple :** supprimer test ou attestation faute de script. Nombre de sections, durée, seuil et données appartiennent au projet.

## Choisir les activités

Choisir selon l'apprentissage, puis déterminer le moyen dans [capacites.md](capacites.md). Le manque d'un générateur ne justifie pas de changer de véhicule pédagogique.

| Besoin | À privilégier et quand | Exemple / contre-exemple |
|---|---|---|
| Jouer, s'exercer sans conséquence | **H5P intégré dans la description de section**, activité source furtive si nécessaire, sans enjeu de note | Anticipation et retour immédiat / entraînement H5P sur un écran séparé |
| Évaluer en formatif ou sommatif | **Test natif autocorrigé**, tentatives, note, seuil et relecture adaptés | Mini-scénarios de transfert / Question Set retenu comme épreuve parce que son générateur existe |
| Atelier, laboratoire, exercice pratique | **Devoir avec remise d'une trace**, corrigé ou non ; fichiers de départ joints à la consigne | Capture ou fichier remis / Page d'atelier cochée manuellement |
| Lexique | **Glossaire** | Recherche par terme / longue Page de définitions |
| Contenu à lire | **Description de section d'abord** ; Page pour une longue lecture ; Livre rarement, pour une longue référence à plusieurs chapitres | Trois étapes dans la section / Livre de six paragraphes répartis en chapitres |
| Document à télécharger et utiliser | **Word ou PDF mis en forme**, jamais `.txt` sauf licence | Fiche à remplir / carnet brut `.txt` |
| Leçon | **À éviter** : écrans et retours au cours multipliés | H5P intégré pour pratiquer sans enjeu / Leçon retenue car automatisée |

### Nombre de tests

Par défaut, prévoir le **test final du socle**, pas un test natif par module. L'entraînement courant passe par les H5P intégrés. Ajouter un jalon formatif seulement à une étape importante : décision, risque ou objectif qui nécessite un résultat mesuré avant de poursuivre. **Tout test supplémentaire est justifié dans le tableau obligatoire de phase 1**, avec sa charge, son objectif et l'alternative écartée ; le responsable valide ce choix. Il n'existe pas de quota universel.

Exemple : un jalon avant une manipulation à conséquences, puis le test final ; contre-exemple : sept tests parce qu'il y a sept modules. Une répétition d'entraînement sans enjeu reste un H5P intégré.

Un autre besoin, par exemple discuter dans un Forum, reste à justifier par sa fonction. Une exception se présente au responsable avec son effet sur le parcours. La capacité technique Leçon reste disponible pour un besoin explicitement validé ; elle n'en fait pas le défaut de conception.

Dans le **plan du responsable**, indiquer objectif, justification, action/trace, retour, suivi, prérequis et réalisation : scripts éprouvés, interface Moodle ou développement restant. Un paquet H5P n'est pas une intégration suivie. Le [contrat v5](contrat-experience-v5.md) fournit Glossaire et pratique avec pièces de consigne ; consulter ses prérequis et l'étape complémentaire de restauration des termes.

## Visuel et suivi

Reprendre par défaut direction visuelle **et attestation** du cours de référence approuvé. Sans référence, explorer la direction sur la section pilote. Produire une maquette par section ; Bootstrap sert la réalisation sans imposer son apparence.

La section garde le contenu utile et des titres courts. L'action précède l'explication de la coche. Un Devoir à achèvement sur remise ne fait pas attendre une correction ; un Devoir à réussite exige un résultat suffisant. Une coche dessinée n'est pas une preuve fonctionnelle.

## Portée

Le cours est un produit utilisable pour l'apprenant ; statuts et limites vont dans le projet du responsable. Utiliser une voie autorisée pour les activités sans générateur, faire valider les adaptations et vérifier les fonctions avant de les promettre.

**Statut : documenté seulement.** La réalisation et les essais appartiennent à chaque cours. Voir l'[exemple de plan](../assets/exemple-plan-cours.md).
