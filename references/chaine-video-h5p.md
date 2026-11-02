# Construire une vidéo interactive ou un questionnaire H5P

Lire cette référence pour encoder une copie vidéo, préparer un VTT ou fabriquer un paquet **Interactive Video / Question Set**. Pour l'intégration dans les sections et le suivi Moodle, lire ensuite la référence dédiée ; un paquet valide hors ligne n'atteste pas la note ou l'achèvement dans Moodle.

## Réutiliser une vidéo et illustrer les manipulations

Avant une nouvelle production, examiner une vidéo existante en ligne : intégration dans la description de section, ou ressource URL si nécessaire. Un éditeur H5P peut accepter une source en ligne compatible, selon fournisseur et version ; l'essayer sur le site autorisé. Les scripts inclus attendent des médias locaux : la possibilité dans un éditeur n'est pas une entrée URL de `construire_h5p.py`. Ne pas télécharger une vidéo sans droits ni autorisation.

Vérifier disponibilité sous rôle apprenant, sous-titres, intégration autorisée et dépendance au service. Prévoir des captures annotées et une consigne textuelle pour les manipulations. Exemple : réutiliser une démonstration accessible et montrer la commande à repérer ; contre-exemple : exiger une vidéo neuve ou laisser un cadre vide.

Voir [Moodle : vidéo](https://docs.moodle.org/501/en/Video) et le [guide Interactive Video](https://h5p.org/tutorial-interactive-video). Ces sources expliquent des voies d'édition, pas une preuve de leur fonctionnement dans le site cible.

## Prérequis et portée

Python ≥ 3.13. FFmpeg est requis pour encoder ou générer une affiche ; fournir `--ffmpeg` ou `FFMPEG_EXE` s'il n'est pas dans le PATH. Aucun téléchargement de vidéo ni envoi vers un service externe n'est effectué. La transcription initiale n'est pas créée par ces scripts : fournir un brouillon VTT issu d'un outil autorisé, puis le relire avec la vidéo.

Les bibliothèques et leurs libellés viennent de paquets de référence intégrés dans un `.mbz` choisi explicitement. Leur présence dans une sauvegarde ne prouve pas qu'elles sont installées sur le site cible. Vérifier les versions et faire accepter les paquets par Moodle avant de déclarer la chaîne opérationnelle sur ce site.

Tous les livrables doivent avoir un nouveau chemin. Les originaux et les fichiers déjà présents ne sont pas écrasés. Les répertoires temporaires d'extraction sont courts. Les chemins de médias dans une fiche sont relatifs à la racine `--projet` et doivent y rester.

### Obtenir et pointer les outils

Versions utilisées pour les tests du 2026-11-01 : Python 3.14.2, FFmpeg 7.1 (build Windows « essentials » de gyan.dev) et PHP CLI 8.5.12. Ce sont des versions de preuve, pas une recommandation de figer indéfiniment ces versions ni une garantie d'identité binaire entre distributions.

- Python : [téléchargements officiels](https://www.python.org/downloads/), puis vérifier `python --version`.
- FFmpeg : partir de la [page officielle de téléchargement](https://ffmpeg.org/download.html), qui renvoie aux fournisseurs de binaires Windows, notamment gyan.dev. FFmpeg fournit lui-même le code source ; un binaire tiers doit être identifié comme tel. Choisir une distribution comprenant les codecs requis par le script et noter version/empreinte.
- PHP pour les tests et le CLI : [téléchargements officiels PHP](https://www.php.net/downloads.php), build adapté au système, puis vérifier `php --version`. Sous Windows, le ZIP CLI peut être extrait dans un répertoire utilisateur ; vérifier les prérequis du build. Le PHP d'un futur Moodle devra aussi convenir à sa version, ce que les tests par doublure ne démontrent pas.

Conserver les outils hors du dépôt et hors d'un dossier temporaire susceptible d'être purgé. Vérifier les empreintes publiées lorsqu'elles sont disponibles. Aucune installation ni modification permanente du PATH n'est nécessaire pour pointer un exécutable déjà préparé. Exemple PowerShell, à adapter au lieu d'extraction réel :

```powershell
$env:FFMPEG_EXE = "$env:LOCALAPPDATA\mcb-outils\ffmpeg\bin\ffmpeg.exe"
$env:PHP_BIN = "$env:LOCALAPPDATA\mcb-outils\php\php.exe"
Test-Path -LiteralPath $env:FFMPEG_EXE
Test-Path -LiteralPath $env:PHP_BIN
& $env:FFMPEG_EXE -version
& $env:PHP_BIN --version
python -B -m unittest discover -s tests -v
```

Les chemins illustrés ne sont pas créés par la skill. FFmpeg peut aussi être fourni par `--ffmpeg` ou découvert dans le PATH ; `PHP_BIN` sert aux tests PHP. Examiner les tests ignorés : un bilan vert avec FFmpeg ou PHP absent ne démontre pas la même couverture que les essais complets. PHP n'est pas requis pour fabriquer uniquement un H5P.

## 1. Préparer une copie MP4

```text
python scripts/encoder_videos.py original.mov --sortie copies --ffmpeg <ffmpeg>
python scripts/encoder_videos.py original.mov --debut 10 --fin 40 --nom extrait --sortie copies
```

Profil par défaut adapté aux démonstrations d'écran : H.264 CRF 30, preset slow, tune stillimage, 15 images/s, yuv420p, au plus 1920×1080 sans agrandissement, AAC 64 kbit/s mono si le son existe, faststart et métadonnées retirées. Paramètres exposés : `--crf`, `--fps`, `--preset`, `--audio-kbps`. Ce profil n'est pas une règle pour toute vidéo : vérifier lisibilité des interfaces, textes, mouvements et son. Les sources sans audio sont admises.

Le test réel vérifie les propriétés d'une courte vidéo synthétique et préserve l'original. La reproductibilité binaire d'un encodage entre versions/plates-formes n'est pas présumée. Pour une comparaison de paquets, réutiliser les copies vidéo existantes.

## 2. Nettoyer les sous-titres

```text
python scripts/nettoyer_vtt.py brouillon.vtt relu-a-preparer.vtt --corrections corrections.json
```

Le fichier de corrections appartient au projet, pas à la skill :

```json
[["mot mal transcrit", "mot attendu"]]
```

Le nettoyeur accepte des répliques WebVTT simples, des identifiants, des horodatages avec ou sans heures et des réglages de réplique. Il écrit en UTF-8/LF, répartit les longues répliques selon le texte, conserve les commentaires NOTE et refuse les constructions non gérées (notamment STYLE/REGION) plutôt que les perdre silencieusement. `--largeur` (42 par défaut) et `--lignes` (2) règlent l'habillage ; un mot trop long n'est pas coupé.

Les phrases suspectes telles que « Merci » ne sont pas des hallucinations démontrées : leur suppression n'est activée que par `--retirer-hallucinations`. Relire orthographe, vocabulaire, chronologie, durée et synchronisation. Ne pas renettoyer automatiquement des VTT déjà corrigés par une personne.

## 3. Décrire le contenu par JSON

Une fiche contient `identifiant` (lettres/chiffres/tirets/underscores), `titre` et `titre_activite`.

Pour **InteractiveVideo** (type implicite ou `"type":"InteractiveVideo"`) : `video`, `sous_titres`, `fin` en secondes, `interactions` triées par temps. Facultatifs : `description`, `affiche_temps` (0 par défaut), `signets` (`[[temps,"libellé"]]`), `fin_libelle`. Les chemins sont relatifs au projet.

Langue facultative : `langue_sous_titres` (ex. `en`, `fr-CA`) et `libelle_sous_titres` (ex. `English`, `Français canadien`). Les options `--langue-sous-titres` et `--libelle-sous-titres` fournissent les replis ; chaque champ présent dans la fiche est prioritaire sur son repli CLI. Sans valeur : code `fr` et libellé `Français` ; pour une autre langue sans libellé, le code est affiché. Le code suit un sous-ensemble syntaxique de BCP 47 : deux ou trois lettres puis éventuels segments alphanumériques de 2 à 8 caractères ; cela ne valide pas un registre de langues complet. Les libellés doivent être non vides, sans caractère de contrôle.

Le code alimente `srcLang` et le suffixe du VTT (`<identifiant>.<langue>.vtt`), le libellé alimente la piste et son choix par défaut. Le fichier VTT source est copié sans transformation ; ces paramètres ne traduisent pas ses textes. Une fiche française historique sans nouveau champ conserve sa piste `fr` et ses noms de fichiers.

La [fiche Interactive Video synthétique](../assets/exemple-video-interactive.json) montre une vidéo fictive de 120 secondes, un VTT, trois signets et trois interactions différentes : MultiChoice, TrueFalse et DragText. Sa structure est vérifiée avec `valider_fiche`, comme la [fiche Question Set](../assets/exemple-question-set.json). Les fichiers `medias/demonstration-fictive.mp4` et `.fr.vtt` ne sont pas fournis : copier la fiche dans le projet et adapter chemins, durées, signets et questions aux médias réels avant fabrication. Une validation de fiche ne vérifie ni l'existence ni la durée réelle des médias, ni les bibliothèques de référence, ni le fonctionnement dans Moodle.

Pour **QuestionSet** :

```json
{
  "type": "QuestionSet",
  "identifiant": "validation",
  "titre": "Validation",
  "titre_activite": "Questionnaire de validation",
  "introduction": "Répondez aux questions.",
  "seuil": 70,
  "retro_globale": [[0,69,"À revoir"],[70,100,"Réussi"]],
  "questions": [{
    "type": "MultiChoice", "cle": "choisir-reponse", "titre": "Exemple", "question": "Choisissez une réponse.",
    "reponses": [
      {"texte":"Option A","correct":true,"retro":"Réponse attendue."},
      {"texte":"Option B","correct":false,"retro":"À revoir."}
    ]
  }]
}
```

Types d'interactions actuellement constructibles :

| Type | Champs spécifiques |
|---|---|
| `MultiChoice` | `question`, `reponses` : `texte`, booléen `correct`, `retro` ; au moins deux options et une correcte |
| `TrueFalse` | `question`, booléen `correct`, `retro_bonne`, `retro_mauvaise` |
| `DragText` | `consigne`, `texte` avec mots délimités par `*`, `distracteurs` facultatifs |

Chaque question a un `titre`. En vidéo, elle a aussi un `temps`. Les autres formes H5P observées dans les sources ne sont pas annoncées comme générées par ce script. Un Question Set H5P est distinct d'un test natif Moodle et de sa banque de questions. Le seuil H5P ne remplace pas le réglage de passage et d'achèvement Moodle.

### Clés et UUID reproductibles

Fournir une `cle` unique par interaction ou question, composée de lettres/chiffres ASCII, tirets ou underscores, commençant par une lettre ou un chiffre. L'UUID version 5 dépend de l'identifiant de fiche et de cette clé dans un espace de noms fixe ; il ne dépend ni de sa position, ni du temps, ni du texte. Garder ces clés lors d'une correction du même élément. Une clé dupliquée ou invalide est refusée avant publication.

Sans clé, l'élément conserve le comportement historique (UUID version 4 aléatoire) et le constructeur émet un avertissement sur stderr. Une fiche mixte est admise, mais son `content.json` complet n'est pas reproductible. Avec toutes les clés et les mêmes entrées/références, les essais synthétiques produisent un `content.json` identique octet pour octet ; le ZIP complet peut conserver des différences de dates.

La langue ne participe pas au calcul : mêmes identifiant de fiche et clés donnent les mêmes UUID entre variantes linguistiques. Changer l'identifiant de fiche permet de distinguer deux ensembles logiques. L'effet sur les tentatives d'activités copiées ou mises à jour reste à vérifier dans Moodle.

## 4. Construire les paquets

```text
python scripts/construire_h5p.py fiches/video.json fiches/test.json --projet <racine-projet> --mbz <reference.mbz> --reference-video <motif-video> --reference-questionnaire <motif-test> --sortie <nouveau-dossier> --ffmpeg <ffmpeg>
```

Les motifs sélectionnent le nom d'un `.h5p` dans `files.xml` : chaque motif doit conduire à un contenu unique. Les alias de même empreinte ne constituent pas plusieurs contenus. Une référence déclarée mais non intégrée, un motif ambigu, un type absent du gabarit ou un média manquant provoque un refus. Le `.mbz` de référence doit actuellement être TAR/gzip. Ne pas déduire le rôle de la sauvegarde de son seul numéro de cours ou nom de fichier.

`--limite-mio` impose une limite facultative : un paquet trop gros est refusé, sans changer silencieusement la qualité. Aucune limite institutionnelle n'est codée dans le script. `--affiches <dossier>` permet de réutiliser des images existantes nommées `<identifiant>-affiche.jpg` ; sinon FFmpeg produit une affiche 1280×720 depuis la vidéo. Les affiches sont des copies, sans modification de la vidéo.

Le constructeur copie les bibliothèques sans le contenu pédagogique du modèle, vérifie leurs manifestes, les dépendances déclarées et les chemins de médias, puis publie un nouveau paquet. Les UUID `subContentId` suivent la politique de clés ci-dessus. Lors d'une non-régression historique sans clés, comparer le contenu après normalisation des seuls UUID et fins de ligne, les manifestes et les empreintes des bibliothèques/médias. Pour des fiches entièrement à clés, comparer aussi le contenu sans retirer les UUID. Ne pas normaliser les réponses, seuils, temps ou autres valeurs fonctionnelles pour masquer un écart.

## Validation et limites

Les scripts sont éprouvés par tests synthétiques, encodage local et reconstruction de huit paquets existants. Les résultats détaillés du cas réel restent dans le projet de développement ; aucun média ou contenu institutionnel n'est fourni avec la skill.

Ces contrôles ne prouvent ni la validité sémantique de toutes les versions de bibliothèques, ni l'accessibilité réelle des interactions, ni la transmission de notes, ni une restauration Moodle. Tester ensuite import, lecture, sous-titres, soumission, note et achèvement dans l'environnement autorisé.

## Maintenance d'un H5P déjà utilisé

Avant de remplacer le paquet d'une activité qui possède déjà des tentatives, conserver son état et vérifier le comportement en environnement autorisé. L'effet des nouveaux UUID sur le rapprochement des anciens résultats est une hypothèse signalée lors de la revue, pas un défaut reproduit dans Moodle.

Le mode à clés permet désormais la stabilité hors ligne. Ajouter une clé à un ancien élément sans clé ne conserve pas son ancien UUID aléatoire ; cette migration exige donc son propre essai. Changer l'identifiant de fiche ou la clé change l'UUID : choisir de nouvelles valeurs pour un nouvel élément logique, et définir dans le projet la politique de copie/nouvelle activité/mise à jour. La reproductibilité des identifiants ne démontre pas la continuité des tentatives ni l'équivalence pédagogique d'une question modifiée.
