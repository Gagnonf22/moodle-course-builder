# Modèle de cours par défaut

Utiliser ce modèle en phase 1 de la [démarche de cocréation](conception-cours.md). Il distingue un **socle par défaut** et un **parcours de sections adapté aux objectifs**. Le plan confirme le socle ou justifie chaque écart pour validation humaine ; il explique aussi les choix d'activités et leur mode réel de fabrication.

## Socle par défaut

| Élément par défaut | À préciser dans le plan et à vérifier |
|---|---|
| Section d'accueil | Objectifs, parcours, durée indicative, préparation, aide et explication du suivi |
| Achèvement expliqué avant chaque activité requise | Action attendue, condition qui déclenche la coche, retour et éventuelle attente ; état constatable après l'action |
| Évaluation finale avec seuil de réussite | Forme adaptée à la compétence, seuil justifié, méthode de notation et de passage, retour et modalités de reprise explicites |
| Attestation après réussite | Composant `customcert` disponible, modèle et restrictions configurés, accès refusé/autorisé et PDF à essayer |
| Rétroaction sur la formation | Feedback ou Questionnaire selon besoin et composants ; identification/anonymat, obligations et visibilité à décider |

Décider explicitement si la rétroaction conditionne l'attestation. Une évaluation finale peut prendre la forme d'un test, d'un H5P ou d'une production évaluée si cela démontre les objectifs ; préciser alors comment le seuil est appliqué et vérifié. Éviter de supposer qu'un seuil H5P règle le passage Moodle, qu'une activité intégrée envoie automatiquement une note ou qu'une réussite émet seule un PDF.

Le nombre de sections, la durée, le seuil et les contenus appartiennent au projet. Ne pas imposer les valeurs d'un cours antérieur. Les sources, identifiants et médias réels ne sont pas des ressources à distribuer avec la skill.

## Proposer les contenus et activités des sections

Relier objectif → ressource/démonstration → action → trace → rétroaction → achèvement. Un même objet peut couvrir plusieurs fonctions. **Aucune vidéo H5P n'est imposée dans chaque section.** Choisir la forme selon le contenu et le travail attendu, sans réduire les possibilités à H5P/Page/Fichier.

| Besoin | Choix possible à justifier dans le plan |
|---|---|
| Comprendre une manipulation avec des retours pendant la démonstration | Vidéo H5P si les interactions servent les objectifs et si des médias adaptés existent ou peuvent être produits |
| Réaliser et démontrer un travail | Devoir avec remise et correction, accompagné des ressources nécessaires |
| Consulter une référence longue | Livre ou Pages pour structurer l'information et faciliter sa consultation |
| S'entraîner avec notation spécialisée | Test natif et types exacts plutôt que conversion simplificatrice en H5P |
| Contribuer ou discuter | Glossaire ou Forum, avec contribution et retour définis |
| Composant absent du site | Proposer un moyen adapté ou annoncer l'impossibilité ; ne pas présenter une autre activité comme équivalente sans examen |

Pour chaque activité ou ressource proposée, indiquer : objectif servi, choix et justification, action/trace attendue, suivi, prérequis et **mode de réalisation**. Distinguer ce que la skill fabrique, ce qui reste à créer manuellement dans Moodle et ce qui nécessiterait un développement ou un outil supplémentaire à vérifier. Un paquet H5P fabriqué n'est pas encore une activité Moodle créée, intégrée et suivie.

Choisir un Livre ou un Devoir plutôt qu'une vidéo n'est pas un écart au socle. En revanche, proposer l'absence d'évaluation finale ou d'attestation modifie le socle : expliquer la raison, la solution et les effets, puis obtenir la validation. Une proposition n'est pas un choix déjà approuvé. Voir l'[exemple de plan](../assets/exemple-plan-cours.md).

## Visuel et suivi

Le modèle ne prescrit pas l'apparence graphique de Bootstrap. La phase 3 établit une direction UX/visuelle puis une maquette par section. Chaque activité requise explique en amont l'action qui conduit à l'achèvement et permet d'en constater ensuite l'état, y compris l'attente ou le verrou lorsque pertinent. Une image de coche ne vaut pas preuve fonctionnelle.

## Limites d'automatisation

Le modèle décrit le cours à produire, pas toutes les fonctions déjà générées par les scripts. Les activités sans générateur sont à créer manuellement dans Moodle dans l'état actuel des capacités, sauf moyen autorisé dont la disponibilité et la portée ont été établies ; voir [capacites.md](capacites.md). Si une capacité manque, annoncer le travail nécessaire avant de promettre sa réalisation.

**Statut : documenté seulement.** L'acceptation du modèle est une décision de conception ; sa réalisation et ses essais sont propres à chaque cours.
