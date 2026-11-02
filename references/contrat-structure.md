# Contrat local `cours/structure.json` — versions 1 à 4

**2026-11-01 : vérifié en Moodle 5.1.8+ local pour H5P/Page/Fichier/attestation ; Feedback/Questionnaire contrôlés par doublures seulement.** Ce contrat décrit les attentes du vérificateur ; il n'annonce pas un générateur pour tous ses types. Lire [automatisation.md](automatisation.md) avant une exécution. Exemple synthétique : [exemple-structure.json](../assets/exemple-structure.json).

## Structure et correspondance

Objet racine : `version: 1` (implicite pour les anciens projets), `sections` tableau ordonné dès la section 0, `image_count` nombre d'images d'aperçu (défaut 1). Le vérificateur exige cours masqué et suivi actif. Chaque section porte `name` et `activities` dans l'ordre exact attendu. Chaque activité porte `type`, `name`, `completion` et, recommandé, `idnumber` unique correspondant à l'identifiant du module après restauration. Les identifiants numériques ne sont jamais repris d'un autre site.

| Type | Champs et contrôles |
|---|---|
| `h5p` (module Moodle `h5pactivity`) | `package` chemin relatif au projet ; empreinte SHA-1, note maximale 100, `gradepass` seuil sur 100 (défaut 0) |
| `page` | `images` noms simples facultatifs ; nombre, liens de fichier et contenu de plus de 200 caractères, hérités du prototype |
| `resource` | `file` chemin relatif au projet ; empreinte du fichier |
| `customcert` | `idnumber` obligatoire ; `condition` = idnumber d'une activité du plan en achèvement `pass` ; `condition_state` vaut 1 (achevé, défaut identique au générateur) ou 2 (réussi, option explicite pour une restriction configurée ainsi). Restriction exacte unique `&`, condition completion, affichée. Vérification des deux comptes ci-dessous |
| `feedback` | Présence dans sa table ; `availability` JSON attendu (défaut null : aucune restriction) ; `submit` contrôle aussi `completionsubmit` |
| `questionnaire` | Plugin distinct, présence dans sa propre table et restriction attendue ; achèvement `none`, `manual` ou `view` recommandé, pas de règle de soumission inventée |

`completion` : `none`, `manual`, `view`, `grade`, `pass`, ou `submit` pour Feedback uniquement. Les réglages automatiques de vue, note et réussite sont contrôlés. Une valeur de mode n'est pas une preuve d'achèvement d'un apprenant. `course_required` booléen choisit si l'activité compte dans les critères du cours (défaut : tout sauf `none`) ; le vérificateur contrôle leur **nombre**, pas encore l'identité de tous les critères.

Le constructeur lit en plus `fullname`, `shortname`, `summary` HTML, `image` chemin, `author` facultatif ; chaque section : `summary` chemin HTML ; chaque activité : `intro` HTML, et `html` chemin pour Page. Images Page sous `images-cours/`. En version 1, il ne fabrique que H5P/Page/Fichier et refuse les autres types avant création. Le contrat peut donc décrire un cours complété manuellement ou par retouche ; **ne pas passer l'exemple complet au constructeur pour espérer créer l'attestation ou la rétroaction**. Les chemins et contenus proviennent du projet de confiance ; validation JSON exhaustive et confinement des chemins historiques restent à renforcer avant un usage non maîtrisé.

## Version 2 : Livre et Devoir

La version 1 (y compris implicite) conserve ses champs et ses types historiques. Pour fabriquer Livre ou Devoir, déclarer `version: 2` ; chaque activité du contrat v2 exige un `idnumber` unique non vide. Le constructeur accepte H5P/Page/Fichier et les deux types ci-dessous ; les autres types restent refusés avant création. `image` devient facultatif : sans image, indiquer `image_count: 0` pour le vérificateur. Le cours et les sections gardent les autres champs de construction ci-dessus.

| Type | Champs v2 et limites |
|---|---|
| `book` | `chapters` : tableau ordonné non vide de `{title, html, subchapter?}`. `html` est un chemin de fichier HTML sous le projet, existant et confiné ; `subchapter` booléen, faux par défaut, interdit sur le premier chapitre. Achèvement `none`, `manual` ou `view`. Chapitres visibles ; import de médias incorporés non fourni |
| `assign` | `submission: {text: bool, files: bool, maxfiles?: entier positif, maxbytes?: entier positif}` ; au moins un canal actif. Défauts : 1 fichier, 1 Mio. `grade` positif, `gradepass` entre 0 et grade, strictement positif si `completion: pass`. `grading` obligatoire : guide ou grille ci-dessous |

Devoir : `completion` accepte `none`, `manual`, `submit`, `grade` ou `pass`. **`pass` ne se termine pas à la remise** : sans note, l'état est incomplet ; après correction insuffisante, échoué ; après note suffisante, réussi. `submit` exige uniquement une remise et ne remplace pas une exigence de réussite. Le profil construit une remise individuelle sans étape de brouillon supplémentaire, sans dates, sans nouvelle tentative automatique, sans notification et avec commentaire de correction. Groupes, échéances, échelles, fichiers de retour et annotations PDF ne sont pas configurables dans ce profil.

`grading: {method: "rubric", name, description?, criteria: [...]}` : chaque critère porte `description` et au moins deux `levels: [{score, definition}]`. Scores distincts non négatifs, un niveau zéro et un maximum positif obligatoires. Moodle convertit la somme des niveaux en note sur `grade`.

`grading: {method: "guide", name, description?, criteria: [...]}` : chaque critère porte `description`, `maxscore` positif, et éventuellement `shortname` et `markers` (consigne de correction). Moodle convertit le total en note sur `grade`. Les définitions sont rendues disponibles à la correction par leurs contrôleurs natifs, sans importer de notes antérieures.

Exemple d'activité synthétique (à insérer dans les `activities` d'une section v2) :

```json
{"type":"assign","idnumber":"trace-pratique","name":"Ma réalisation","intro":"<p>Remettre une trace et expliquer sa vérification. La coche exige au moins 75/100 après correction.</p>","completion":"pass","grade":100,"gradepass":75,"submission":{"text":true,"files":false},"grading":{"method":"rubric","name":"Correction de la trace","criteria":[{"description":"Résultat expliqué","levels":[{"score":0,"definition":"Absent"},{"score":1,"definition":"Partiel"},{"score":2,"definition":"Complet"}]}]}}
```

Le vérificateur compare les chapitres (ordre, titres, sous-chapitres, contenu, visibilité), les canaux et limites de remise, la consigne, le maximum et le seuil, puis la méthode et les critères/niveaux de correction après remappage. Il ne soumet ni ne corrige un travail. Après inscription d'utilisateurs fictifs pour l'essai, `--apprenants=<fichier privé JSON>` évite le contrôle « aucun inscrit » ; cela ne prouve pas leurs résultats de Devoir. Ceux-ci doivent être vérifiés séparément par l'API et le parcours apprenant.

**Essai v2 du 2026-11-01, Moodle 5.1.8+ local :** Livre et trois Devoirs construits, sauvegardés sans participants puis restaurés ; vérificateur réussi. Remises texte, fichier et mixte par un étudiant fictif, corrections par un enseignant fictif via les API natives, attente et notes/achèvements observés. Navigation apprenant/correcteur et deux chapitres contrôlés séparément. Cette extension a été contre-validée indépendamment le 2026-11-01.

## Version 3 : banque et test natif

La version 3 conserve les capacités v2 et ajoute `qbank`/`quiz`. Lire le [contrat des tests natifs](contrat-tests-natifs.md) pour les quatre types de questions, les références de banque, fractions, tolérances et réglages de relecture. L'exemple synthétique s'y trouve. Le constructeur refuse ces types en v1/v2, et une référence à une banque absente ou déclarée après le test avant toute création.

Les banques ne contribuent pas à l'achèvement ; les notes/réussites du test sont contrôlées comme les autres activités notées. Le vérificateur vérifie les questions et leurs références après restauration mais ne crée aucune tentative ; les preuves de notation et d'achèvement des apprenants sont recueillies séparément.

## Version 4 : Feedback, Leçon, attestation native

La version 4 conserve les capacités v1 à v3 et ajoute la fabrication des trois familles selon le [contrat parcours/rétroaction v4](contrat-parcours-v4.md). Feedback possède des éléments, un anonymat explicite et une seule réponse ; Leçon associe les sauts à des clés de pages et peut employer `completion: end` ; l'attestation native exige un PNG de projet et une condition de réussite précédente. Les limitations des profils et les exemples sont dans cette référence.

Le vérificateur contrôle éléments et réglages, pages et sauts remappés, format/éléments/contexte/fichier de l'attestation. Les envois Feedback, le parcours de Leçon et l'émission PDF restent des essais distincts. `end` est automatique et réservé à la Leçon ; ce n'est pas le simple mode `view`.

## Deux états de l'attestation

Dans une instance locale autorisée, préparer **manuellement** deux comptes d'essai distincts, inscrits actifs, sans droits administratifs, gestion d'activités ou contournement des restrictions. Réaliser l'évaluation : un compte échoue (état d'achèvement 3), l'autre réussit (état 2). Ne pas écrire artificiellement ces états en base pour obtenir un succès.

Fichier privé séparé `apprenants.json` : `{"echec": 101, "reussite": 102}` (identifiants fictifs à remplacer par ceux de cette instance). Le script vérifie les inscriptions, les privilèges, l'état d'achèvement enregistré, puis appelle l'API de disponibilité pour **chaque utilisateur explicitement**. Sans les deux comptes, le résultat est incomplet, code 1, et non une réussite statique.

```text
php scripts/moodle/verifier_cours.php --validation-locale --moodle=<racine-contenant-config.php> --courseid=<id-local> --projet=<projet> --apprenants=<apprenants.json>
```

Codes : 0 contrôles réussis ; 1 contrôle échoué/incomplet ; 2 précondition refusée (une erreur PHP non interceptée reste aussi non nulle). Aucune émission de PDF n'est provoquée. L'API vérifie la restriction de l'activité, **pas l'intégralité de l'accès au cours, de la section ou du plugin**. Un cours masqué peut interdire la navigation aux apprenants : organiser l'essai navigateur sur le site de validation avec les droits et la visibilité approuvés. Essayer réellement refus d'accès, réussite, téléchargement PDF, signature et rétroaction ; ne pas confondre ce parcours avec la sortie du CLI. Les appels de lecture Moodle peuvent initialiser des caches ; aucun résultat, note ni achèvement n'est créé par ce script.

Source d'API : [disponibilité et userid explicite](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/availability/classes/info.php), [conditions d'achèvement](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/availability/condition/completion/classes/condition.php). Dans Moodle 5.1, `e=1` admet achevé/réussi et refuse échoué ; `e=2` exige réussi. Le générateur conserve `e=1` du profil éprouvé historiquement, sans changer silencieusement le prototype ; les essais restent nécessaires pour la version cible.
