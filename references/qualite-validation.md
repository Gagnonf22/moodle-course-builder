# Vérifier le cours à la bonne échelle

Lire pour préparer les essais d'un livrable ou diagnostiquer un écart. Choisir les contrôles qui couvrent les fonctions touchées ; ne pas rejouer une validation exhaustive pour une correction de texte sans effet fonctionnel.

## Relecture de l'expérience

À chaque phase, appliquer les points UX de [la démarche](conception-cours.md) : KISS, choix d'activités, titres, séparation des deux publics et contenu propre à l'étape. En phase 4, relire sections et activités comme un apprenant, avant toute livraison : dépliants et boutons non vides, médias présents, pas de code interne ni de note de chantier, consignes regroupées, remise réelle pour la pratique. Exemple : la trace et la coche annoncées correspondent ; contre-exemple : Page cochée supposée prouver une remise.

Un contrôle automatique de signalements est prévu mais non livré à ce stade. Il ne remplacera ni la relecture ni l'essai. Les réserves techniques, captures d'essai et statuts vont dans les fichiers du responsable ; ils ne s'affichent pas dans le cours. Les liens suivent la [convention documentée](concevoir-section.md#liens-et-changements-donglet), distincte d'une obligation WCAG.

Pour le futur contrôle automatique, **séparer les champs analysés** : contenu des sections et activités pour les répétitions, en excluant menus et navigation ; noms complets/abrégés du cours et titres d'activités contrôlés à part. Exemple : un titre répété dans le menu n'est pas une répétition rédactionnelle ; un code de chantier dans le nom abrégé reste un signalement. Cette exigence d'étalonnage est prévue pour U3, pas implémentée ici.

## Avant l'instance

Contrôler les fichiers et liens, formats attendus, intégrité des médias, dépendances et paramètres fonctionnels. Relire les questions et sous-titres sur le fond. Les scripts de la chaîne ont des tests locaux ; leur succès ne remplace ni la relecture pédagogique ni un essai Moodle.

Pour comparer une reconstruction, définir à l'avance les écarts de représentation admissibles. Sur les H5P reconstruits, l'ordre des clés JSON, les fins de ligne et les UUID `subContentId` sont traités séparément des réponses, temps, seuils et médias. Ne pas supprimer de champs fonctionnels pour obtenir artificiellement une égalité.

## Dans l'environnement autorisé

Conserver un moyen de retour adapté à l'opération. Sur un essai de parcours, utiliser un véritable compte apprenant de test : la prévisualisation administrateur peut contourner des restrictions. Pour comparer réussite et échec, choisir des comptes ou états séparés qui n'héritent pas des mêmes traces.

| Fonction touchée | Vérification observable |
|---|---|
| Navigation et ressources | Atteindre la section et les contenus prévus ; liens, images et fichiers utilisables |
| H5P | Lire, afficher les sous-titres, interagir, remettre ; examiner tentative, note et achèvement séparément |
| Test natif | Remettre une tentative, vérifier score calculé, relecture, passage et sélection de questions |
| Devoir | Déposer, finaliser selon les réglages, corriger, recevoir le retour et voir l'état attendu |
| Enquête | Refus d'une obligation omise, réponse acceptée, résultats accessibles aux bonnes personnes |
| Dépendance | Accès refusé ou permis selon les états prévus, sans verrou circulaire |
| Attestation | Accès avant/après admissibilité, PDF téléchargé et contenu vérifié |
| Restauration | Objets destination autonomes, fichiers/références résolus, parcours essentiel encore fonctionnel |

Ne rechercher une trace technique xAPI, une règle cron ou un événement serveur que si cela explique le défaut ou fait partie de l'exigence ; l'absence d'un tel contrôle n'annule pas les observations effectivement réalisées.

## Visuel et accessibilité

Appliquer la phase 3 de [conception-cours.md](conception-cours.md) : direction visuelle choisie sur la section pilote, puis maquette de chaque section. Deux ou trois directions sont proposées lorsqu'une direction nouvelle est nécessaire ; la direction et l’attestation du cours de référence approuvé sont reprises par défaut. Une variante légère pour sections répétitives nécessite également cet accord.

Identifier version, format, thème et comportement de l'éditeur avant de choisir des classes ou composants. Bootstrap 5 ne doit pas être présumé. Après sauvegarde, rouvrir le HTML pour voir ce que l'éditeur a conservé ; les scripts et composants interactifs d'une maquette ne sont pas automatiquement fonctionnels dans Moodle.

L'expérience utilisateur guide les choix ; les composants du thème et de Bootstrap servent à réaliser la direction retenue, sans imposer leur apparence par défaut. Utiliser des titres sémantiques, liens explicites, textes alternatifs utiles, contraste lisible et sous-titres relus. Vérifier le clavier et le focus pour les actions principales, la lisibilité sur petit écran et le téléchargement des documents. Ne pas placer les consignes essentielles uniquement dans une illustration.

Chaque maquette utilise le texte du brouillon validé et montre les vues écran/mobile et les états utiles. Les médias provisoires sont identifiés au responsable, hors du contenu final de l’apprenant. Montrer les états pertinents : avant/après achèvement, attente ou verrou si pertinent. Pour chaque activité requise, l'action et le déclencheur de la coche sont compréhensibles en amont ; l'état obtenu peut être constaté ensuite. Une attente de correction humaine ne doit pas être présentée comme une coche immédiate.

Conserver dans le projet les **captures du rendu réel** : fournies par le responsable dans son site, ou automatiques dans un Moodle local quand l’environnement le permet. Un blocage de capture n’autorise pas son contournement ; le thème local peut différer. Les captures du site cible restent la validation finale du rendu. Identifier pour le responsable ce qui est simulé et ce qui est vérifié ; ne pas superposer les réserves au cours. L'essai visuel précoce de la section pilote vérifie le rendu et la conservation par l'éditeur ; la phase 4b vérifie le fonctionnement du cours complet. Faire approuver une adaptation qui change une maquette déjà validée.

Préférer les composants disponibles et styles autorisés ; une modification du thème ou du CSS global exige un périmètre de déploiement distinct du contenu éditorial. [Thèmes Moodle](https://moodledev.io/docs/5.0/apis/plugintypes/theme), [Bootstrap, si la version est applicable](https://getbootstrap.com/docs/5.3/).

### HTML Bootstrap et repli sans JavaScript

Pour produire le HTML Bootstrap, utiliser la skill `moodle-bootstrap-content` **si elle est disponible** et pertinente dans l'environnement ; lire ses instructions avant de l'employer. Sa présence n'est pas présumée et aucune installation automatique n'est requise. Sans cette skill, préparer le HTML compatible avec les possibilités vérifiées du thème en conservant la direction UX approuvée.

L'hypothèse selon laquelle l'éditeur retire les attributs `data-bs-*` doit être vérifiée **sur le site cible**, après enregistrement et réouverture du contenu ; elle n'est pas un comportement universel démontré de Moodle. Un composant dépendant de JavaScript peut aussi échouer pour une autre raison. Ne pas laisser un bouton qui paraît actif alors que son contenu n'est plus accessible.

Pour un simple contenu à déplier, proposer ce repli natif sans JavaScript ni attribut `data-bs-*` :

```html
<details>
  <summary>Comment vérifier ma progression ?</summary>
  <p>Consultez la condition annoncée avant l'activité, puis vérifiez son état après votre action. Si une correction est nécessaire, l'état peut rester en attente.</p>
</details>
```

Le couple `details`/`summary` fournit un mécanisme HTML de dévoilement ; conserver le libellé explicite et le comportement natif, sans ajouter de faux rôle ou masquer le focus. Ce motif n'est pas un remplacement d'onglets, de menus ou d'un suivi Moodle. [Standard HTML : details](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-details-element).

Vérifier conservation par l'éditeur, ouverture/fermeture au clavier, focus visible, lecture du libellé et de l'état avec les aides techniques pertinentes, et rendu mobile. Ces propriétés restent à essayer dans le site ; le fragment seul n'est pas une certification d'accessibilité. Si `details`/`summary` est aussi retiré ou inadapté, proposer un titre suivi du contenu toujours visible. Faire valider l'adaptation d'une maquette approuvée avant de la décliner.

## Bilan

Pour chaque fonction importante, indiquer résultat attendu, observation, environnement et limite restante. Décrire le défaut reproduit plutôt que déclarer tout le cours incompatible. Un rapport doit permettre de distinguer une construction hors ligne réussie d'une fonction testée en instance.

Les sources éditables, décisions et preuves du cours restent dans son projet. Pour étendre la skill, promouvoir uniquement une connaissance générale étayée ; la trace complète d'une enquête de développement n'est pas une instruction à charger pour chaque cours.
