# Tests Moodle et banques de questions

Lire pour une activité `quiz` et sa banque. Un Question Set H5P et l'activité de sondage Questionnaire sont des objets distincts. Le constructeur local fournit un profil [banque qbank et test natif, contrat v3](contrat-tests-natifs.md) pour quatre types ; les autres passent par une interface ou un outil autorisé. Aucun exporteur générique Moodle XML/GIFT/QTI n'est inclus.

## Choisir pour évaluer, pas seulement pour fabriquer

Utiliser le Test natif autocorrigé pour le formatif et le sommatif ; l'entraînement sans conséquence passe par un H5P intégré dans la section. La disponibilité d'un générateur ne choisit pas l'activité.

- Privilégier de **nouveaux mini-scénarios de transfert**, plutôt que recopier la tâche ou la réponse de l'atelier.
- Éviter la **réponse courte**, sauf si l'orthographe exacte est l'objet de l'évaluation ; ne pas exiger un libellé arbitraire pour vérifier une compréhension. Conserver les types existants et leurs sémantiques lors d'une reprise autorisée ; une modification d'épreuve doit être validée.
- À la relecture, expliquer pour chaque distracteur pourquoi une personne pourrait le choisir. Retirer les réponses manifestement absurdes et les indices de longueur, de ton ou de formulation.
- Rétroaction générale propre à chaque question, ou absente si celle des réponses suffit. Chaque retour aide à comprendre l'effet du choix ; éviter un même paragraphe générique copié partout.
- Garder un nombre de choix cohérent dans une même série ; justifier une variation par la tâche. Ne pas ajouter un distracteur ridicule pour atteindre un nombre. Ne pas imposer quatre choix à tous les formats.

**Exemple :** après l'atelier de comparaison de versions, présenter une situation nouvelle : « Une collègue a écrasé une valeur ; quelle première vérification faites-vous ? » avec des actions plausibles et un retour par réponse. **Contre-exemples :** reproduire exactement l'atelier ; demander de saisir un libellé au caractère près ; proposer « Le prix le plus élevé garantit la qualité ». Les données d'exercice ne justifient pas un bandeau « fictif » dans l'énoncé.

## 1. Décrire le test et ses questions

Définir objectifs, couverture, notation et rétroaction avant de choisir les types. Pour chaque question, conserver dans le projet : clé, type et version du composant, énoncé, médias, réponses attendues, barème, rétroactions, indices et paramètres spécifiques. Pour une petite série, un tableau ou des fiches suffisent ; ne pas imposer une nouvelle banque canonique à un projet déjà structuré.

Relire séparément la justesse du contenu : consigne autonome, réponse défendable, distracteurs plausibles, absence d'indices involontaires et charge de lecture adaptée. Une grande diversité de types n'améliore pas à elle seule le test.

| Famille rencontrée | Exemples de types | Paramètres à préserver ou à vérifier |
|---|---|---|
| Choix et réponses sélectionnées | `multichoice`, `truefalse`, `oumultiresponse` | Réponse unique/multiple, fractions, pénalités, mélange, rétroactions ; comportements différents selon le type |
| Texte et rédaction | `shortanswer`, `essay`, `essayautograde` | Casse et variantes admises, correction humaine/automatique, format et pièces jointes |
| Numérique et calcul | `numerical`, `calculated`, `calculatedsimple`, `calculatedmulti`, `formulas`, `algebra`, `numericalrecit` | Tolérances, unités, variables, jeux de données, fonctions et moteur requis |
| Association et ordonnancement | `match`, `randomsamatch`, `ordering`, `ddmatch` | Couples, ordre, banque source, notation partielle et comportement de glissement |
| Lacunes et zones | `multianswer`, `gapselect`, `gapfill`, `ddwtos`, `wordselect`, `ddimageortext`, `ddmarker` | Syntaxe interne, groupes, zones, images, coordonnées et variantes acceptées |
| Extensions WIRIS | `shortanswerwiris`, `multianswerwiris`, `truefalsewiris` | Moteur et paramètres propres au plugin ; ne pas réduire au type de nom voisin |
| Information | `description` | Présentation sans réponse évaluée ; ne pas la compter comme preuve de compétence |

Ce tableau reprend les 28 libellés observés, sans affirmer une classification native/extension identique entre versions. Vérifier le composant installé et ses options. Les données et corrections disciplinaires des exemples sources restent dans les projets.

## 2. Créer ou reprendre la banque

Identifier la banque, son contexte, les catégories et les droits. Dans le profil Moodle 5.1, la banque est un module `qbank` standard masqué, les questions appartiennent à son contexte de module ; ne pas les déposer directement dans le contexte du cours. Déclarer banque et références de questions dans le contrat v3. Créer les questions dans le type exact disponible ou importer un fichier prévu pour ce site. Prévisualiser chaque type et tester une réponse correcte, incorrecte et les cas qui changent le score : réponse partielle, tolérance limite, indice ou tentative supplémentaire.

Pour reprendre une sauvegarde, compter les questions au niveau des versions principales de chaque entrée de banque. Les sous-questions Cloze/WIRIS font partie d'une question composée ; une recherche récursive de toutes les balises `question` produit des faux types et faux totaux. Une banque peut être présente sans être utilisée par aucun test du cours.

## 3. Construire le test

Créer l'activité puis y ajouter les questions ou sélections prévues. Vérifier les emplacements, catégories et versions réellement utilisées ; noter les références dynamiques qui peuvent modifier la sélection. Une banque importée ne remplit pas automatiquement le test.

Régler explicitement tentatives, temps si pertinent, navigation, comportement des questions, mélange, calcul de la note et moments de relecture. Définir quand les réponses et rétroactions deviennent visibles. Le passage et l'achèvement sont à configurer séparément. [Réglages du test](https://docs.moodle.org/501/en/Quiz_settings).

Essayer une tentative entière sous le rôle apprenant : début, navigation, validation, remise et relecture. Contrôler le score attendu et ses effets dans le carnet et l'achèvement. Pour une question calculée, vérifier plusieurs instanciations lorsque le tirage modifie les réponses.

## Import, export et conversion

Choisir le format selon le type et l'importeur du site ; Moodle XML est un format de questions, pas une sauvegarde de cours. Ne pas renommer `questions.xml` issu d'un `.mbz` pour en faire un fichier d'import : les structures ont des fonctions différentes. [Format Moodle XML](https://docs.moodle.org/501/en/Moodle_XML_format).

Avant une conversion, dresser la correspondance des champs source/destination : réponse, notation, tolérance, rétroaction, média, jeu de données et paramètres du plugin. Si une sémantique n'est pas représentable, conserver la source et signaler la perte ; ne pas la remplacer par une question plus simple sans accord. Un format tiers n'est pas un passage obligatoire.

Sur un petit échantillon représentatif autorisé, importer, prévisualiser et vérifier la notation ; exporter ensuite si un aller-retour est requis et comparer les valeurs fonctionnelles. La validité XML seule ne prouve ni l'acceptation par Moodle ni l'équivalence de notation.

**Preuve du 2026-11-01, Moodle 5.1.8+ local :** banque/test construits, sauvegardés/restaurés puis vérifiés ; cinq questions couvrant choix unique/multiple, vrai/faux, courte et numérique. Deux tentatives natives sous étudiant fictif, par API : 5/7 puis 7/7, achèvement échoué puis réussi au seuil 75 %. Réponse numérique 10,6 refusée et 10,4 acceptée pour 10 ± 0,5 ; `BLEU` accepté sans distinction de casse. La saisie et la relecture dans l'interface, les frontières de tolérance et les autres types restent à essayer. Les observations du corpus ne valent pas fabrication de tous ses types.
