# Contrat v5 — ressources et progression

Le contrat v5 conserve les versions 1 à 4. Il ajoute les capacités ci-dessous ; elles ne changent pas les règles pédagogiques de tous les cours. Les nouveaux champs sont refusés dans un contrat ancien. Lire [le contrat commun](contrat-structure.md) et [les conditions locales](automatisation.md) avant exécution.

## Description de section et H5P

Chaque section garde `summary`, chemin d'un fichier HTML UTF-8 confiné dans le projet. Titres, tableaux, encadrés, listes et compléments facultatifs sont conservés ; le vérificateur compare le HTML complet après construction et restauration. Ce contrôle n'est pas un audit d'accessibilité ou du rendu du thème.

En v5, un `h5p` d'entraînement est intégré par défaut dans sa section et sa véritable activité source reste disponible sans affichage direct dans la liste. Un H5P en `completion: "pass"` n'est pas intégré par défaut ; le booléen `embed` permet un choix explicite. Les versions antérieures gardent leur affichage historique.

Placer `{{h5p:cle-activite}}` dans le HTML pour choisir l'emplacement. Sans marqueur, l'intégration est ajoutée à la fin de la description. Une clé inconnue, un marqueur répété ou un marqueur visant un H5P non intégré est refusé avant création. Les contextes et liens sont résolus dans le cours courant puis recalculés par le vérificateur après restauration.

Les activités furtives doivent être autorisées dans le site local et prises en charge par le format ; le constructeur refuse leur absence de configuration de site avant de créer le cours. Le filtre d'affichage H5P et les bibliothèques nécessaires doivent être disponibles. Le script n'active pas ces composants. Ne pas annoncer que tous les chemins d'intégration transmettent une note sans essai apprenant.

## Glossaire

**Destination utilisateur :** aucune installation Moodle ni exécution de CLI à demander. Le script de reprise ci-dessous est réservé au développement. Ce contrat ne fournit pas encore un fichier d'import natif des termes testé pour l'utilisateur ; fournir les définitions et annoncer une saisie manuelle ou une voie d'import à vérifier dans son Moodle existant. Cette limite ne doit pas être masquée par une promesse de `.mbz` autonome.

```json
{"type":"glossary","idnumber":"lexique","name":"Comprendre les repères",
 "intro":"<p>Les termes du parcours.</p>","completion":"none",
 "entries":[{"concept":"Trace","definition":"<p>Production permettant de constater une action.</p>"}]}
```

Profil : dictionnaire, termes uniques, définitions HTML non vides, entrées approuvées créées par l'API native, sans notation ni liaison automatique. Achèvement `none`, `manual` ou `view` disponible techniquement ; choisir celui du plan. Pas de catégories, pièces jointes d'entrée ou médias incorporés dans ce profil.

**Limite native importante :** Moodle 5.1 omet les entrées du Glossaire lorsque la sauvegarde est faite sans utilisateurs. Le constructeur v5 transporte donc aussi les seules définitions du modèle, sans auteurs ni traces, dans `entrees-modele.json`, zone de fichiers `mod_glossary/intro`, incluse dans la sauvegarde native.

Après restauration native sans utilisateurs dans un **cours local masqué**, exécuter l'étape complémentaire :

```text
php scripts/moodle/restaurer_glossaires.php --moodle=<dossier config.php> --courseid=<cours restauré> --validation-locale
```

Elle relit ce fichier et recrée les entrées par l'API native. Elle ne remplace aucune entrée : un Glossaire existant identique est laissé intact ; un Glossaire non vide divergent entraîne un refus avant les ajouts. Cette étape ne s'applique qu'aux définitions du modèle transportées par ce constructeur ; ce n'est pas une sauvegarde des contributions des apprenants. Le vérificateur contrôle les définitions finales et le fichier portable.

Une restauration Moodle seule ne suffit donc pas pour ce profil. Pour une destination où ce CLI local n'est pas disponible, prévoir une importation native des termes ou une autre réalisation autorisée et vérifiée ; ne pas annoncer un `.mbz` autonome restaurant automatiquement les termes dans tout site. Aucun réglage d'inclusion des utilisateurs n'est assoupli par le script.

## Devoir de pratique

En v5, `grade: 0` permet un Devoir sans note, sans champ `grading`. Choisir `completion: "submit"` pour l'achèvement à la remise. Les canaux texte et/ou fichier et leurs limites restent ceux du contrat v2. Une remise n'est pas une évaluation de qualité. La possibilité d'un retour textuel Moodle ne rend pas sa correction obligatoire.

`attachments` est une liste facultative de chemins de fichiers sous le projet : ils sont joints à la consigne dans la zone native des fichiers supplémentaires du Devoir. Les chemins absents, hors projet ou les noms de fichiers en collision sont refusés. Le vérificateur compare noms, nombres et empreintes après restauration. Les Devoirs notés conservent leur guide ou grille historique ; `grade: 0` est incompatible avec achèvement à la note/réussite et avec un barème.

## Test remis et réussite distincte

Les réglages de banque, questions et relecture du [contrat des Tests](contrat-tests-natifs.md) restent applicables. En v5 :

- `attempts: 0` signifie tentatives illimitées ; un entier positif conserve une limite. Les versions anciennes continuent de refuser zéro.
- `completion: "submit"` configure au moins une tentative **terminée**, sans exiger sa réussite pour l'achèvement. Une tentative ouverte ne suffit pas. Le seuil reste dans `gradepass` et peut servir séparément à l'accès à une attestation.
- Les modes `grade` et `pass` restent disponibles avec leur sens antérieur. L'épuisement des tentatives n'est jamais activé comme repli de réussite.

## Attestation à plusieurs conditions

Le champ historique `condition` reste supporté. En v5, on peut lui substituer une liste non vide `conditions`, sans mélanger les deux formes :

```json
"conditions": [
  {"type":"completion","activity":"pratique","state":1},
  {"type":"completion","activity":"test","state":1},
  {"type":"grade","activity":"test","min":75}
]
```

Toutes les conditions sont conjointes (**ET**), visibles et ciblent des activités précédentes du même contrat. `state: 1` exige un achèvement actif ; `state: 2` exige une activité en mode `pass`. `grade.min` est un nombre de 0 à 100, en pourcentage de l'élément de note de l'activité cible ; ce n'est pas une valeur brute sur un autre barème. Devoir sans note exclu des conditions de note. La remise et la réussite d'un même Test peuvent ainsi être deux conditions distinctes.

Le constructeur résout séparément identifiants de modules et d'éléments de note. Le vérificateur reconstitue la restriction avec les identifiants du cours restauré. Aucun seuil universel n'est imposé ; ne pas confondre cette restriction avec les critères globaux d'achèvement du cours.

Pour un contrôle d'accès réel, `--apprenants` peut désigner un JSON contenant `cases`, liste de `{userid: entier, allowed: booléen}`. Les comptes doivent être des apprenants inscrits sans privilèges d'édition ou de contournement. Les cas doivent couvrir échec, réussite avec condition manquante et toutes conditions remplies. Sans ces cas, le vérificateur annonce l'accès comme **À valider** ; les contrôles structurels ne prouvent pas le parcours.

## Preuves et limites

Les essais, versions et résultats détaillés sont indiqués dans [les capacités](capacites.md). Tester le parcours apprenant, le PDF et le rendu séparément. Le transport des définitions de Glossaire et la création de médias sont deux problèmes distincts ; aucune vidéo ni bibliothèque n'est ajoutée à la distribution par ce contrat.
