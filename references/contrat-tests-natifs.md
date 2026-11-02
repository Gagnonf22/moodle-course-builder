# Contrat v3 — banque qbank et test natif

Extension de [structure.json](contrat-structure.md), pour Moodle 5.1. Les versions 1 et 2 restent acceptées pour leurs capacités existantes. Déclarer `version: 3` pour ces deux nouveaux types. Chaque activité garde les champs communs `idnumber`, `name`, `intro` et `completion`. Aucun identifiant numérique d'une autre instance n'est repris.

## Banque

Activité `type: "qbank"`, `completion: "none"`, `course_required: false`, avec `questions` non vide. Déclarer la banque **avant les tests qui s'y réfèrent**. Le constructeur crée un module qbank standard masqué, sans achèvement : ce n'est pas une activité d'apprentissage à cocher. Les questions sont placées dans sa catégorie par défaut, dans le contexte du module, et sauvegardées par les API des types natifs, avec leurs entrées et versions prêtes.

Chaque question porte :

- `key` : chaîne stable unique dans cette banque, enregistrée comme idnumber de l'entrée de banque ;
- `type` : `multichoice`, `truefalse`, `shortanswer` ou `numerical` ;
- `name`, `text` (énoncé HTML), `mark` (nombre strictement positif), `generalfeedback` HTML facultatif ;
- les champs propres au type ci-dessous.

| Type | Champs et notation |
|---|---|
| `multichoice` | `single` booléen obligatoire, `shuffle` booléen facultatif (faux). `answers` contient au moins deux `{text, fraction, feedback?}`. Texte HTML et fraction numérique entre -1 et 1. Choix unique : exactement une fraction 1, autres fractions non positives. Choix multiple : somme des fractions positives égale à 1 ; pénalités explicites dans les fractions négatives, jamais ajoutées implicitement |
| `truefalse` | `correct` booléen obligatoire ; `feedbacktrue` et `feedbackfalse` HTML facultatifs. Chaque réponse vaut 0 ou 100 % selon ce booléen |
| `shortanswer` | `usecase` booléen facultatif (faux), `answers: [{text, fraction, feedback?}]`. Au moins une fraction 1 ; texte de réponse simple et joker Moodle conservé. Ordre des réponses préservé |
| `numerical` | `answers: [{text, fraction, tolerance, feedback?}]`. `text` chaîne numérique finie, `tolerance` nombre absolu non négatif ; au moins une fraction 1. Pas d'unité, jeu de données, formule ou conversion depuis un type calculé |

Les fractions et points du contrat sont des nombres JSON, pas des chaînes. La correction est celle du moteur Moodle. Les types non pris en charge sont refusés, sans les transformer en QCM. Médias incorporés, indices, versions historiques, tirages aléatoires, sous-catégories et types de plugins ne sont pas fabriqués par ce profil.

## Test

Activité `type: "quiz"`, avec :

- `bank` : idnumber du module qbank précédemment déclaré ;
- `questions` : tableau ordonné de clés de cette banque, sans doublon ; il peut sélectionner un sous-ensemble ;
- `attempts` : entier positif ; `grademethod` : `highest`, `average`, `first` ou `last` ;
- `grade` : maximum positif, `gradepass` : seuil entre 0 et ce maximum ; seuil positif exigé en achèvement `pass` ;
- `completion` : `none`, `manual`, `grade` ou `pass` ;
- `review` : relecture explicitement décrite ci-dessous.

Le profil construit un test à rétroaction différée, sans minuterie ni restriction temporelle, navigation libre, une question par page. Le poids de chaque emplacement est `mark` de sa question ; la somme est recalculée par le calculateur natif. Les références utilisent les entrées de banque et leur dernière version, comme l'ajout natif ; une future modification de banque peut donc changer la version utilisée par une nouvelle tentative. Aucun scénario de maintenance de tentatives n'est garanti par ces essais.

`review` contient des objets de phase `during`, `immediately`, `open`, `closed`. Chaque objet accepte les booléens `attempt`, `correctness`, `maxmarks`, `marks`, `specificfeedback`, `generalfeedback`, `rightanswer`, `overallfeedback`. Champ omis : faux. Phase/champ inconnu ou valeur non booléenne : refus. `during.attempt` doit être vrai et `during.overallfeedback` faux. Moodle peut rendre certains réglages inopérants selon le comportement choisi ; vérifier l'affichage réel avant livraison.

```json
{"during":{"attempt":true,"maxmarks":true},"immediately":{"attempt":true,"marks":true,"specificfeedback":true,"generalfeedback":true},"open":{"attempt":true,"marks":true},"closed":{"attempt":true,"marks":true,"rightanswer":true}}
```

Exemple complet synthétique : [exemple-test-natif.json](../assets/exemple-test-natif.json). Le placer en `cours/structure.json` dans un projet de test autorisé et créer le fichier de résumé HTML mentionné ; choisir un nom abrégé neuf. Les sources de questions restent dans le projet.

## Vérifier et annoncer la preuve

Le vérificateur compare les questions prêtes et leur contexte qbank, énoncés, notes, réponses, fractions, rétroactions, casse, choix unique/multiple, mélange et tolérances. Pour le test, il compare les réglages de relecture et notation, les références vers la banque du cours restauré, l'ordre et les poids des emplacements. La seule présence d'une banque ne prouve pas son utilisation par le test ; la comparaison porte sur ces références.

Le vérificateur ne démarre pas de tentative. Réaliser séparément un parcours fictif autorisé et comparer notes et achèvements réels, par API natives ou navigateur en le précisant. Une réponse numérique dans la tolérance et une hors tolérance sont deux cas distincts ; ajouter les frontières exactes si le besoin le justifie.

**2026-11-01, Moodle 5.1.8+ local :** banque et cinq questions couvrant les quatre types, dont choix unique et multiple, construites puis sauvegardées/restaurées ; vérificateur réussi. Deux tentatives sous un étudiant fictif via API natives : 10,6 hors de 10 ± 0,5 donne 5/7 et achèvement 3 ; 10,4 donne 7/7 et achèvement 2 au seuil 75/100. Casse indifférente éprouvée par `BLEU`. Cela ne constitue pas un essai de l'interface de réponse, des limites exactes ou de toutes les méthodes de notation.

**Sources d'API consultées :** code Moodle 5.1 installé, `question/type/questiontypebase.php`, types natifs concernés, `mod/qbank/lib.php`, `mod/quiz/locallib.php`, `mod/quiz/classes/quiz_attempt.php` et `grade_calculator.php`. Aucun générateur de tests PHPUnit utilisé par les scripts livrés.
