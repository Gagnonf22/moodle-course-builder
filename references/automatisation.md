# Choisir une voie d'automatisation

Lire avant une action via API, connecteur, navigateur ou script privilégié. Partir des fonctions réellement disponibles ; ne pas déduire une capacité d'écriture d'un nom d'outil ou d'un export Moodle.

| Voie | Ce qu'il faut établir | Limite |
|---|---|---|
| Interface Moodle | Rôle, capacité dans le cours, composants et options accessibles | Le compte enseignant n'est pas un compte d'administration |
| Services externes existants | Service activé, fonction exposée, identité, contexte, schémas d'entrée/sortie | Un jeton ne donne pas toutes les fonctions ; gérer les erreurs Moodle même en réponse HTTP réussie |
| Connecteur/MCP | Opérations exposées dans la session et périmètre du compte | Aucune liste de fonctions supposée à partir d'un ancien dépôt GitHub |
| PHP CLI local | Instance et base isolées, autorisation d'essai, préconditions du script | Privilèges élevés ; les scripts fournis ne sont pas des outils de production |
| Nouveau plugin ou nouvelle fonction serveur | Mandat de développement, contrôle d'accès, déploiement autorisé | Chantier distinct de la simple création de cours |

## Appeler un service existant

Lire le contrat de la fonction correspondant à la version cible : types, paramètres obligatoires, contexte et résultat. Commencer par les lectures nécessaires pour identifier les bons objets. Garder les jetons hors des fichiers partagés, URL d'exemple et journaux. Le transport de fichiers est une opération distincte de la création d'activité.

Pour une écriture autorisée, définir l'objet et le résultat attendu, exécuter puis relire. En cas de délai ou d'erreur ambiguë, vérifier si l'objet existe déjà avant de réessayer ; éviter les doublons. Les nouvelles fonctions serveur exigent leur propre validation de paramètres, de contexte et de droits ; ne pas les présumer installées. [API des services externes](https://moodledev.io/docs/apis/subsystems/external).

## État des scripts PHP fournis

Le constructeur crée un cours masqué et refuse une collision de nom abrégé ; il exige `--validation-locale` et une URL en boucle locale. Il traite H5P, Page et Fichier à partir de `cours/structure.json`, avec des choix hérités du prototype ; le [contrat version 2](contrat-structure.md) ajoute Livre et Devoir individuel avec grille ou guide ; le [contrat v3](contrat-tests-natifs.md) ajoute qbank et quiz pour quatre types natifs ; le [contrat v4](contrat-parcours-v4.md) ajoute Feedback, Leçon et attestation native. Le [contrat v5](contrat-experience-v5.md) ajoute Glossaire, pièces de consigne et pratique sans note, intégration H5P, HTML riche contrôlé, tentatives illimitées et conditions multiples. Après restauration native sans utilisateurs, `restaurer_glossaires.php` reprend les seules définitions du modèle transportées dans la sauvegarde, sans écraser un Glossaire divergent. Le vérificateur couvre davantage de familles que le constructeur, qui refuse les types non fabriqués avant création.

**Avant tout usage réel :** établir l'isolation effective de l'instance, de la base et des fichiers, vérifier le contrat d'entrée et les chemins, puis valider les API sur l'instance locale d'essai autorisée. Elle peut être persistante si elle reste isolée, arrêtée hors usage et munie d'un état propre de secours. Le garde-fou `dbhost` est ajouté en 3a et testé par doublure ; il refuse hôte distant/absent et valide explicitement le socket local. Il agit après le bootstrap `config.php` et ne prouve ni l'absence de tunnel ni l'isolation de toute la configuration. Le constructeur et le sauvegardeur passent en compte administrateur dans leur chemin normal ; un essai local ne crée aucune autorisation sur un autre site.

Le vérificateur exige aussi les garde-fous locaux. Il contrôle H5P/Page/Fichier, Livre/Devoir, qbank/quiz, Leçon, attestation et Feedback/Questionnaire selon les versions du contrat. Les résultats des Devoirs et tests natifs restent des essais séparés. Pour l'attestation historique, deux comptes d'essai avec échec/réussite doivent être préparés manuellement : contrôle des états enregistrés et appel de l'API de restriction pour chaque compte. Pour les conditions multiples v5, fournir plutôt des cas d'accès attendus dans `--apprenants`, selon le contrat v5 ; le contrôle de structure seul annonce les accès comme À valider. Il ne vérifie ni toutes les familles, ni l'ergonomie, ni l'émission PDF. Les tests unitaires PHP reposent sur une doublure sans base. En complément, M1 a éprouvé création, sauvegarde, restauration et vérification H5P/Page/Fichier/attestation sur Moodle 5.1.8+ local, Custom certificate 5.0.11 (2026-11-01) ; M2a/M2b ont étendu et éprouvé Livre/Devoir et banque/test natif ; M2c a éprouvé Feedback/Leçon et attestation native dans leurs profils. Questionnaire reste testé par doublure seulement. Le parcours navigateur et le PDF sont des essais séparés, pas des fonctions du vérificateur.

Le sauvegardeur natif local exige cours masqué, sortie neuve `.mbz` et `users=0`. Les exclusions actives verrouillées provoquent un refus. Il impose `activities`, `blocks`, `filters`, **`files` et `contentbankcontent` à 1**, même si les défauts du site les désactivent ; un de ces réglages verrouillé à 0 provoque un refus. Ces réglages racine sont définis dans [backup_root_task de Moodle 5.1](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/backup/moodle2/backup_root_task.class.php). Il produit une copie par lecture du fichier natif, sans supprimer le résultat conservé par Moodle. Ce réglage exclut les données d'usage selon Moodle, **pas les renseignements éventuellement présents dans les textes, médias ou métadonnées du contenu**. Examiner la composition avant tout partage. Cette sauvegarde sans participants ne convient pas au retour arrière d'un cours en production avec participants.

```text
php scripts/moodle/sauvegarder_cours.php --validation-locale --moodle=<racine-contenant-config.php> --courseid=<id-local> --fichier=<sortie-neuve.mbz>
```

Le fichier de sortie est réservé exclusivement puis rempli : en cas d'interruption brutale, une sortie partielle peut rester ; ne pas la traiter comme livrée. Répertoire privé de confiance exigé, pas de résistance annoncée à une substitution concurrente malveillante. Codes 0 succès de l'export, 2 refus/erreur ; contrôler ensuite l'archive et sa restauration. Sources d'API : [contrôleur natif](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/backup/controller/backup_controller.class.php), [lecture du fichier stocké](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/lib/filestorage/stored_file.php).

Les commandes historiques et les tests se trouvent dans [mbz-retouches-locales.md](mbz-retouches-locales.md), accompagnés de leurs conditions et limites. Les réserves de cette page s'appliquent avant leur usage réel.

## Résultat à annoncer

Décrire séparément fichiers préparés, appel exécuté, objet relu et fonctionnement essayé. Un accès navigateur ne justifie pas une modification de permissions ; une création locale ne justifie pas un déploiement. Les limites de l'outil orientent le choix de réalisation, sans modifier le besoin de l'utilisateur.
