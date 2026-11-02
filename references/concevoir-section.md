# Concevoir une section centrée sur l'action

Lire en phase 1 pour organiser le parcours, puis pendant les brouillons, maquettes et relectures. Appliquer l'[outil de choix](modele-cours-de-base.md#choisir-les-activités) avant de choisir les moyens de fabrication.

## Accueil, identité et noms propres au produit

La **section 0 présente le cours** : bandeau, objectifs d'ensemble, déroulement, durée et conditions de l'attestation. Elle ne commence pas directement par le premier module. Exemple : « Bien démarrer » avec le parcours et la réussite attendue ; contre-exemple : « M00 — Se préparer » sans présentation.

Garder une **structure reconnaissable**, avec une intention et des repères propres au contenu de chaque section : illustration ou icône utile, points « À retenir », disposition adaptée. Exemple : étapes illustrées pour une manipulation, comparaison pour une décision ; contre-exemple : onze encadrés identiques dont seule une ligne change. Ne pas inventer un design différent à chaque section ni ajouter des ornements sans fonction.

Le **nom complet et le nom abrégé du cours** sont lisibles et prêts pour l'apprenant : aucun code d'essai, date de chantier ou numéro de version. Ils apparaissent aussi dans le fil d'Ariane et le titre de l'onglet. Les versions restent dans le projet. Exemple : « Réaliser une tâche numérique » ; contre-exemple : « ESSAI-NUIT-20261102 — v2 ».

## Une page principale, une prochaine action

La **description de section est la page principale** : bandeau (titre, intention, durée indicative), objectifs, points « À retenir », consignes courtes, H5P et vidéos utiles intégrés. Avant chaque activité requise, préciser l'action, le déclencheur de la coche et le retour reçu. Distinguer remise, correction différée et réussite.

KISS : un seul endroit pour agir, peu de clics, d'onglets et de changements de page, sans ajouter de sous-niveaux de navigation. Une activité séparée apporte une fonction : remise, note, suivi ou consultation spécialisée. Sa présence technique n'impose pas une deuxième copie visible du contenu. Pour l'entraînement H5P, l'affichage est dans la section ; l'activité source peut être disponible sans affichage sur la page du cours. Vérifier ses accès et son suivi.

**Exemple :** « Retrouver une version » : durée, trois étapes illustrées, vidéo et entraînement intégrés, puis « Déposez une capture dans le Devoir pour obtenir la coche ; aucune correction n'est attendue ». Configurer et essayer ce dernier comportement.

**Contre-exemple :** section vide → Page « Guide » → Livre de trois paragraphes → fichier isolé → Page « Atelier » à cocher soi-même. Aucun dépôt ne prouve la pratique.

## Titres et finition

- Titres visibles courts, distincts et orientés vers l'action : « Retrouver une version », pas « M03-GUIDE — Atelier — Retrouver une version ». Les clés restent dans le projet et `idnumber`.
- Description et action propres à chaque étape : « Comparez les versions et indiquez la différence », pas « Votre action : réalisez cette étape ». Conserver les libellés fonctionnels communs qui facilitent le repérage, supprimer le remplissage répété.
- Garder les consignes et informations essentielles visibles ; réserver les dépliants aux compléments facultatifs. Une page ne doit pas paraître vide avant ouverture de cinq dépliants.
- Aucun dépliant, onglet ou bouton vide. Un média absent ne laisse ni cadre vide ni invitation à le lire. Faire décider une solution utile dans le projet, puis présenter seulement le parcours utilisable.
- Une mise en garde utile au bon endroit suffit ; ne pas répéter partout le même avertissement. Ajouter une aide locale si le risque change réellement.
- Supprimer titres dupliqués, ponctuation fautive et promesses de navigation non vérifiées. Lecture dans la section d'abord ; document à utiliser en Word ou PDF mis en forme, jamais en `.txt`, sauf licence.

**Exemple :** un Devoir regroupe consigne, fichier de départ et remise ; la section explique son but et l'achèvement. **Contre-exemple :** trois activités pour télécharger, lire l'exercice et déclarer l'avoir fait.

## Deux publics, deux endroits

Le **cours est le produit de l'apprenant** : cas réalistes, informations utiles et actions réalisables. Les données d'exercice peuvent être inventées sans afficher « fictif », « brouillon », « avant l'ouverture » ou une note de chantier. Exclure les données réelles sensibles ; ne pas présenter une invention comme un fait réel cité.

Les **fichiers de projet du responsable** (`LIRE-AVANT-IMPORT.md`, `DECISIONS.md`, sources et bilan) portent provenance, choix, statuts, limites techniques, points à vérifier et états simulés. Ne pas copier ces notes dans les sections, introductions, questions ou attestations. Une attribution exigée, une limite réelle de l'activité ou une information nécessaire pour agir reste présente à l'endroit utile pour l'apprenant.

**Exemple :** cours : « Comparez les offres et justifiez votre choix » ; fichier responsable : « Données d'exercice créées pour ce cas ; accès externe à essayer ». **Contre-exemple :** bandeau apprenant « Cours entièrement fictif ; source et limite : rendu non validé ».

## Médias et captures

Examiner d'abord les médias existants, dont les vidéos en ligne : intégration dans la section en priorité, ressource URL si nécessaire, ou vidéo interactive H5P avec source en ligne si l'éditeur et le fournisseur la prennent en charge. Vérifier accès apprenant, sous-titres, droits, authentification et dépendance externe. Le constructeur de paquets actuel exige des médias locaux ; ne pas lui annoncer une entrée URL non gérée. Voir [la chaîne vidéo](chaine-video-h5p.md).

Fournir **au moins une capture annotée pour chaque manipulation d’interface** : étape, zone à repérer, action, résultat attendu, sans donnée personnelle inutile. Décrire l'action dans le texte aussi.

**Exemple :** vidéo disponible intégrée et capture de la commande encadrée et décrite. **Contre-exemple :** demander systématiquement une nouvelle vidéo ou laisser un dépliant vidéo sans média.

## Liens et changements d'onglet

**Convention de conception :** lien externe dans un nouvel onglet, annoncé par une icône et le texte visible « nouvel onglet » ; lien interne dans le même onglet. Le navigateur peut ouvrir une fenêtre. L'avertissement doit être compréhensible au clavier et au lecteur d'écran ; une icône seule ne suffit pas. Exemple à essayer après enregistrement dans l'éditeur :

```html
<a href="https://example.org/guide" target="_blank" rel="noopener">
  Consulter le guide <span aria-hidden="true">↗</span> (nouvel onglet)
</a>
```

**Contre-exemples :** nouvel onglet sans avertissement ; lien interne ouvrant un autre onglet sans utilité. Limiter les liens externes quand le contenu essentiel peut rester sur place.

Ce choix n'est **pas une obligation WCAG d'ouvrir les liens externes**. Le [critère 3.2.5, niveau AAA](https://www.w3.org/WAI/WCAG22/Understanding/change-on-request.html) traite des changements de contexte demandés ou désactivables. [G201](https://www.w3.org/WAI/WCAG22/Techniques/general/G201) conseille un avertissement visuel et accessible ; cette technique est indicative. [G200](https://www.w3.org/WAI/WCAG22/Techniques/general/G200), également indicative, recommande de limiter les nouvelles fenêtres aux besoins utiles. Si cette convention nuit au public ou à son environnement, faire valider l'adaptation avant de la décliner.

## Direction et attestation

Si un cours de référence est approuvé, reprendre **par défaut sa direction visuelle et son modèle d'attestation**, en adaptant contenu et dépendances. Ne pas substituer un certificat minimal pour faciliter sa fabrication. Si le modèle dépasse le profil natif, choisir une voie compatible ou faire valider l'adaptation ; voir [reconnaissance](suivi-reconnaissance.md).

**Exemple :** conserver hiérarchie, encadrés et composition de l'attestation approuvée. **Contre-exemple :** inventer une nouvelle présentation et remplacer le certificat sans soumettre le changement.

## Relire comme un apprenant

À chaque phase : où commence-t-on, que fait-on, où reste-t-on, qu'obtient-on, que signifie la coche ? Vérifier activités, titres, contenu propre à l'étape, absence de notes au responsable et de composants vides. En 4b, observer le comportement sous rôle apprenant ; une capture ou un XML ne démontre pas l'achèvement.

**Statut : documenté seulement.** Ces règles ne prouvent pas un parcours reconstruit ; les extensions de fabrication demandent leur validation propre.
