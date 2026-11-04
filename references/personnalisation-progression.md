# Accueil personnalisé et progression

Lire pour réaliser une salutation dynamique ou une barre d'avancement. Ces aides facilitent le repérage ; elles ne démontrent pas une compétence acquise.

## Composants du site cible

Le filtre RÉCIT Autolink est `filter_recitactivity`. Le bouton TinyMCE `tiny_recitautolink` aide à insérer ses balises ; le filtre les interprète à l'affichage. Le bouton seul ne remplace pas le filtre. Sources : [filtre](https://github.com/SN-RECIT-formation-a-distance/moodle-filter_recitautolink), [bouton TinyMCE](https://github.com/SN-RECIT-formation-a-distance/moodle-tiny_recitautolink), [annuaire Moodle](https://marketplace.moodle.com/plugins/filter_recitactivity).

Vérifier compatibilité, activation dans le contexte concerné et ordre du filtre avant celui des liens d'activités natif. Une capture ne prouve pas sa disponibilité ailleurs ; une sauvegarde de cours ne transporte pas le code du plugin. Utiliser les composants existants du Moodle cible. Ne demander ni serveur local ni installation de plugin à l'utilisateur pour utiliser la skill ; une intervention d'administration demeure un mandat distinct.

## Salutation

Avec le filtre confirmé actif : `<h2>Bonjour [[d/user.firstname]]</h2>`. Le prénom vient du compte connecté ; ne pas inscrire celui du concepteur dans le modèle. Sans filtre confirmé, livrer « Bonjour » ou « Bienvenue », sans balise brute. La saisie directe de la balise ne nécessite pas le bouton TinyMCE. Ne pas ajouter courriel, avatar ou autres données de profil sans besoin explicite.

Après import, essayer deux comptes distincts pour vérifier que la personnalisation n'est ni figée ni mélangée par un cache.

## Repère de progression du modèle

Prévoir un repère discret lié aux achèvements réels. Expliquer ce qu'il compte : le pourcentage d'activités terminées n'est ni une note ni une mesure de maîtrise. Choisir les conditions d'achèvement selon les actions et preuves prévues au plan.

Le filtre propose une barre de cours :

```html
<p>Votre progression dans les activités suivies</p>
[[cpb/]]
```

Pour une section nommée « Repères » : `[[spb/Repères]]`. Le nom doit correspondre à celui du cours destination ; vérifier après renommage ou restauration. La barre de cours compte les activités considérées suivies par le filtre, pas automatiquement les seules exigences d'attestation ; vérifier ce périmètre avec les activités retenues.

Pendant la passe UX, vérifier que le repère est visible, lisible et utile ; une zone vide ne remplit pas cette demande. Choisir une présentation principale adaptée au parcours : barre intégrée ou bloc de progression déjà disponible. Un bloc latéral est un composant distinct à identifier avant d'en annoncer la fabrication ; la barre du filtre n'en constitue pas une reproduction garantie.

Sans composant compatible, conserver les indicateurs natifs d'achèvement et annoncer ce repli au responsable ; ne pas dessiner une fausse barre statique. Ne pas insérer de barre sans activités suivies : ce cas n'est pas couvert par les essais ci-dessous. Vérifier accès, états initial/intermédiaire/final, clavier et mobile après import dans le Moodle existant de l'utilisateur.

## Preuves et limites

Complément du 2026-11-03 : sur un parcours restauré comprenant Devoir de pratique et Test, les deux activités terminées donnent une barre à 100 % même après échec au Test ; l'attestation reste alors refusée. Une reprise réussie autorise l'attestation si la pratique est remise. Cette observation confirme la distinction entre avancement et réussite ; le périmètre reste à vérifier dans chaque cours cible.

Essais du 2026-11-03 : Moodle 5.1.8+, filtre v2.1.3-stable (`2026091000`), bouton TinyMCE v3.0.2-stable (`2026052002`), dans une instance de développement locale isolée déjà disponible. Deux comptes synthétiques affichent leur propre prénom et leur propre progression ; les barres de cours et de section évoluent de 0 à 50 puis 100 % après consultation de deux Pages suivies. Le bouton TinyMCE ouvre son dialogue et insère la balise du prénom. Cela ne valide ni toutes les fonctions du filtre, ni tous les thèmes, ni la continuité après restauration, ni l'accessibilité complète.

Voir [l'import sans serveur local](sauvegardes.md#parcours-utilisateur-sans-serveur-local) et [la validation du cours](qualite-validation.md).
