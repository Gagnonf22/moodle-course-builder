# Devoirs, remises et correction

**Moyen :** activité native Devoir (`assign`) dans le site autorisé. Le constructeur local inclut un profil individuel texte/fichier avec grille ou guide : [contrat v2](contrat-structure.md). Lire pour demander une production et permettre sa remise, plutôt que publier uniquement une consigne. Pour des réglages hors de ce profil, passer par une interface ou API autorisée sans les supprimer silencieusement.

## Pratiquer et remettre une trace

Tout atelier, laboratoire ou exercice pratique est un **Devoir avec remise d'une trace**, corrigé ou non. Joindre les fichiers de départ à la consigne (fichiers supplémentaires du Devoir) ; ne pas ajouter une ressource Fichier et une Page pour un seul exercice. Le résultat attendu peut être une capture, un fichier ou une explication.

Choisir explicitement : **achèvement à la remise sans correction obligatoire** pour une pratique, ou **achèvement sur réussite** avec note suffisante pour un travail évalué. Dans le premier cas, une trace finalisée peut déclencher la coche sans attente d'un correcteur ; dans le second, montrer l'attente puis le résultat. Ne pas ajouter une grille et une charge de correction par défaut à toute pratique.

Décrire aussi le processus de remise avec les canaux et libellés réellement configurés : obtenir le fichier si nécessaire, réaliser le travail, ouvrir « Ajouter un travail », saisir le texte ou déposer le fichier prévu, enregistrer puis soumettre/confirmer seulement si ces réglages l’exigent. Indiquer comment constater la remise et si la coche attend une correction.

**Exemple, pour une remise de fichier sans confirmation supplémentaire :** « Téléchargez le fichier joint et réalisez l’opération. Cliquez sur Ajouter un travail, déposez votre capture, puis sur Enregistrer. Vérifiez que le fichier apparaît comme remis ; cette remise déclenche la coche ». **Contre-exemple :** Page « Atelier » avec auto-déclaration manuelle, sans canal de dépôt.

Ces règles sont de conception. Le profil actuel doit être consulté dans [capacites.md](capacites.md) et le [contrat](contrat-structure.md) : le [profil v5](contrat-experience-v5.md) fournit les fichiers de consigne et le Devoir sans note à achèvement sur remise, éprouvés localement le 2026-11-03 ; vérifier encore les réglages du cours cible.

## Préparer le contrat de travail

Décrire l'action attendue, le livrable, les critères de réussite, les ressources et le retour prévu. Définir texte en ligne ou fichiers, formats/nombre/taille utiles, travail individuel ou de groupe, dates si nécessaires et modalités de nouvelle remise. Une capture peut témoigner d'une réalisation ; vérifier qu'elle montre ce qui doit être évalué et qu'elle n'expose pas de données inutiles.

## Construire

1. Ajouter le Devoir dans la section prévue et déposer consignes et ressources nécessaires.
2. Activer les canaux de remise voulus ; vérifier les limites du site et les réglages de brouillon/validation. Si le travail est collectif, configurer et essayer les groupes au lieu de supposer qu'un fichier déposé vaut remise pour tous.
3. Choisir la notation et les moyens de retour disponibles : commentaire, fichier, annotation ou autre fonction du site. Séparer ces moyens de retour du mode de remise.
4. Définir l'achèvement : dépôt attendu, note ou autre condition réellement offerte. La consultation de la consigne ne prouve pas une remise.

Ces choix sont décrits dans les [réglages du Devoir](https://docs.moodle.org/501/en/Assignment_settings) ; les plugins de remise et de retour du site peuvent en modifier les possibilités.

## Grille et guide de correction

Choisir une grille (`rubric`) pour des critères avec niveaux descriptifs, ou un guide (`guide`) lorsque la méthode disponible correspond mieux au jugement attendu. Préparer critères, niveaux ou points, descriptions et règle de totalisation. Vérifier leur publication/disponibilité dans le formulaire de correction et les informations montrées à l'étudiant.

Dans une sauvegarde, la seule présence de `grading.xml` ne démontre pas une grille : rechercher la méthode, sa définition effective et son rattachement au Devoir. Une enveloppe vide n'est pas un modèle de barème. Ne pas réutiliser les notes ou commentaires d'anciens participants pour créer un modèle.

## Essai minimal utile

Avec données fictives : déposer sous un rôle apprenant, finaliser si nécessaire, retrouver la remise côté correcteur, appliquer les critères et fournir le retour. Vérifier ensuite note, rétroaction visible et achèvement côté apprenant. Ajouter un cas de dépôt refusé ou incomplet si les limites de remise sont importantes pour le cours.

Pour une restauration, vérifier en plus fichiers de consigne, plugins et définitions de correction ; l'absence volontaire des anciens travaux est normale dans une sauvegarde de modèle sans participants.

**Résultat :** une activité de remise utilisable, une correction seulement si prévue et un retour accessible. La preuve historique ci-dessous porte sur le profil noté. En complément, le 2026-11-03, la pratique v5 sans note avec PDF joint a été sauvegardée/restaurée : remise texte via API native, achèvement constaté sans ligne de correction ; téléchargement et lecture de la pièce PDF par l'apprenant dans le navigateur. Profil local éprouvé le 2026-11-01 sur Moodle 5.1.8+ : construction, sauvegarde/restauration, trois modes de remise, guide et grilles conservés. Remises et corrections effectuées via API natives sous comptes fictifs étudiant/enseignant, sans écriture directe des résultats en base. État remis/non corrigé incomplet ; note insuffisante échouée ; note suffisante réussie. Affichage apprenant et correcteur essayé séparément. Ce succès ne couvre pas les groupes, annotations PDF ni tout paramétrage de Devoir.
