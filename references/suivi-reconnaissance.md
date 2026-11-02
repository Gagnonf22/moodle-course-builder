# Notes, achèvement, accès et reconnaissance

Lire lorsqu'une action doit compter, débloquer une suite ou permettre une attestation. Un score, une condition d'achèvement, une restriction d'accès et une émission de certificat sont des mécanismes distincts.

## Définir les états attendus

Dans le plan du cours, décrire l'action observable et le résultat attendu pour chaque activité suivie : consulter, remettre, obtenir une note, réussir, contribuer ou déclarer manuellement. Choisir une condition offerte par le composant et cohérente avec cette action. Décrire à part les conditions d'achèvement du cours.

Pour une note, préciser maximum, passage et agrégation nécessaires. Un pourcentage configuré à l'intérieur d'un H5P ne règle pas automatiquement le passage Moodle. Une remise de Devoir peut précéder sa correction ; éviter un verrou qui suppose une note instantanée si personne ne la fournit.

Construire les activités référencées avant de configurer les dépendances. Conserver dans le projet un rapprochement clé logique → identifiant Moodle/identifiant de sauvegarde. Vérifier les références entrantes après duplication, suppression autorisée ou restauration. Tester une dépendance non satisfaite et une satisfaite ; rechercher aussi les boucles qui bloquent le parcours.

## Attestation

1. Identifier le composant exact, par exemple `customcert`, et sa version. Il s'agit d'un plugin ; ne pas supposer sa présence.
2. Reprendre par défaut **le modèle d’attestation du cours de référence approuvé**, puis adapter contenu, éléments dynamiques, dépendances et fichiers/polices. Ne pas remplacer ce modèle par une présentation simplifiée pour satisfaire le constructeur. Les noms réels et éléments institutionnels restent dans le projet.
3. Configurer l'accès selon les exigences approuvées : note, achèvement ou autres critères disponibles. Ne pas supposer qu'une note de passage déclenche à elle seule une émission.
4. Essayer l'accès avant admissibilité, puis après. Ouvrir l'activité, télécharger le PDF, vérifier contenu, mise en page et comportement d'un second accès si cela compte pour le besoin.
5. Vérifier séparément les fonctions de vérification publique, de réémission ou de notification si elles sont requises ; ne pas les déduire d'un PDF réussi.

Un téléchargement de PDF a été confirmé par l'utilisateur sur un livrable historique restauré. Cette confirmation ne valide pas un autre générateur ou plugin. Deux moyens sont maintenant fournis : [retouche d'une sauvegarde depuis un modèle explicite](retouches-activites.md) et [création native v4](contrat-parcours-v4.md), limitée à une page/fond PNG/nom/date/code. La voie native convient à un cours neuf seulement si elle conserve le modèle approuvé ou si son adaptation est validée ; la retouche conserve davantage du modèle couvert. Exemple : reprendre la composition approuvée ; contre-exemple : substituer sans accord un certificat minimal avec note de chantier. Les deux voies ont été éprouvées après restauration sur Moodle 5.1.8+ local / Custom certificate 5.0.11 le 2026-11-01, avec échec refusé, réussite autorisée et PDF avec fond. Cela ne garantit ni tous les modèles ni toutes les versions. [Plugin Custom certificate](https://moodle.org/plugins/mod_customcert).

## Badge

Définir sa signification et ses critères si le besoin prévoit une reconnaissance par badge. Vérifier règles d'attribution, visibilité et émission dans le site. Une définition de badge dans une sauvegarde n'est pas une preuve d'attribution à un participant. Un badge ne remplace pas automatiquement une attestation PDF.

## Export partiel

Une sauvegarde d'attestation seule peut encore référencer des modules absents de l'export. Avant réutilisation, inclure ces dépendances ou remplacer les critères par les objets cibles. Ne jamais rendre l'attestation librement accessible pour faire disparaître un problème de références sans décision sur ce changement de sens.

**Sources de contexte :** [achèvement d'activité](https://docs.moodle.org/501/en/Activity_completion), [restrictions](https://docs.moodle.org/501/en/Restrict_access_settings), [badges](https://docs.moodle.org/501/en/Badges). Les réglages précis et le parcours doivent être vérifiés dans le site cible.
