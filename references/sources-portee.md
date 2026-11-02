# Sources et limites de la distribution

Consulter pour vérifier une affirmation technique ou étendre une procédure. Choisir la documentation de la version installée ; les liens ci-dessous ne sont pas une matrice de compatibilité garantie.

## Sources opérationnelles

- [MoodleDocs](https://docs.moodle.org/) : activités, ressources, notes, achèvement, sauvegarde et restauration ; liens précis dans chaque procédure. Les pages 5.1 de réglages Quiz, Devoir, Feedback, format Moodle XML, activités furtives et Questionnaire ont été consultées pour cette refonte le 2026-11-01. Aucun essai en instance n'en découle.
- Les pages 5.1 [restauration](https://docs.moodle.org/501/en/Course_restore#General_restore_defaults) et [sauvegarde](https://docs.moodle.org/501/en/Course_backup#Backing_up_a_course) ont également été consultées le 2026-11-01 : modes fusion/suppression du contenu et options d'inclusion des données utilisateur. Les règles de production sont dans [sauvegardes.md](sauvegardes.md) ; aucun essai destructif ni récupération n'a été effectué.
- [Documentation développeur Moodle](https://moodledev.io/) : contrats des API et extensions ; vérifier la version avant de développer.
- [Répertoire des plugins Moodle](https://moodle.org/plugins/) : composant, version et dépendances ; une fiche ne prouve pas l'installation sur le site cible.
- [Documentation H5P](https://h5p.org/documentation) : contenus et bibliothèques ; vérifier les versions des paquets et de l'intégration Moodle.

## Savoir repris et réécrit

Les procédures réorganisent les distinctions utiles de la version précédente et les modèles observés dans un corpus local de sauvegardes. Seules des connaissances de domaine et des exemples synthétiques sont inclus ici : aucun cours source, inventaire de participants, média institutionnel ou identifiant de cours n'est fourni.

Les principes de sélection du format, de conservation des sémantiques et de revue distincte du contenu étaient déjà rapprochés de sources externes dans la version précédente : [moodle-mcq](https://github.com/danielcregg/moodle-mcq/blob/master/SKILL.md), [qti-question-bank-generator-skill](https://github.com/andreums/qti-question-bank-generator-skill/blob/main/SKILL.md) et [moodle-web-services](https://github.com/SaadRahman01/claude-moodle-dev/blob/main/skills/moodle-web-services/SKILL.md). Aucun code ni extrait de ces sources n'est importé par la refonte. Leur historique de lecture détaillé est conservé dans les archives du développement, pas chargé à chaque usage.

## Portée de la distribution

La refonte documentaire, 2b, 3a, 3b, 3c et les correctifs suivants ont été revus indépendamment hors ligne le 2026-11-01 (80 tests). M1 a ensuite éprouvé une chaîne réelle dans Moodle 5.1.8+ local / Custom certificate 5.0.11 : construction, sauvegarde, retouches, restauration, échec/réussite et PDF avec fond. Deux défauts ont été corrigés après observation en instance : déclaration XML de détection et contexte de cours des images. Les 82 tests et ces ajouts M1 ont depuis été contre-validés indépendamment. Voir la portée et les limites par capacité. L'ancien inventaire détaillé et l'ancien empaqueteur restent exclus ; l'aperçu simple ne remplace pas un inventaire de dépendances.

M1 a depuis été contre-validé indépendamment (82 tests et contrôles de restauration/PDF). M2a ajoute Livre et Devoir avec contrat v2, dans la portée de [capacites.md](capacites.md), contre-validés indépendamment. M2b ajoute banque/test natif, avec preuves et limites dans [contrat-tests-natifs.md](contrat-tests-natifs.md), contre-validés indépendamment (103 tests). M2c ajoute Feedback/Leçon/attestation native selon [contrat-parcours-v4.md](contrat-parcours-v4.md), 114 tests réussis et contre-validation indépendante acquise. Sources d'API consultées dans le code Moodle 5.1 installé : `mod/book/lib.php`, `mod/book/db/install.xml`, `mod/assign/locallib.php` (création, remise, correction), `grade/grading/lib.php` et contrôleurs `rubric`/`guide`. M2c consulte aussi `mod/feedback/lib.php` et les classes d’éléments/formulaire, `mod/lesson/locallib.php` et `customcert` (création de modèle, fabrique d’éléments et restauration). Les essais complètent cette lecture ; ils ne garantissent pas d'autres versions.

La distribution 0.7.0 est proposée sous licence MIT ; voir le fichier LICENSE à la racine. Cette licence ne réattribue pas les droits sur Moodle, ses plugins, les bibliothèques H5P, les médias ou les contenus importés ultérieurement : vérifier leurs licences et autorisations séparément. Aucun cours source ni paquet de bibliothèques tierces n'est fourni.
