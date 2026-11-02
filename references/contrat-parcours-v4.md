# Contrat v4 — Feedback, Leçon, attestation native

Extension de [structure.json](contrat-structure.md), pour l'instance locale autorisée. `version: 4` conserve les profils v1 à v3 ; les champs communs et clés uniques restent obligatoires. Les trois familles ci-dessous ne sont fabriquées qu'en v4. Questionnaire reste un plugin distinct sans générateur.

## Feedback

Activité `type: "feedback"`, `anonymous` booléen obligatoire ; `completion` : `none`, `manual`, `view` ou `submit`. Le profil autorise une seule réponse, sans dates, notification ni publication des statistiques. `submit` signifie envoyer une réponse complète, pas obtenir une note.

`items` : tableau ordonné non vide. Chaque élément contient `key` (lettres/chiffres/tiret/trait bas, unique dans ce Feedback), `type`, `name`, `required` booléen facultatif (faux). La clé est conservée dans le libellé technique natif pour la vérification après restauration.

| Type | Champs et comportement |
|---|---|
| `multichoice` | `choices` : au moins deux textes simples sans saut de ligne ni `|` ; choix unique par boutons radio |
| `textfield` | Réponse courte, limite native du profil : 255 caractères |
| `textarea` | Réponse longue ; cinq lignes affichées, pas de limite de mots ajoutée |
| `info` | `mode: "course"` (défaut) ou `"category"` ; information sur le cours ou sa catégorie, pas une question personnelle |
| `label` | `html` : information HTML affichée ; aucun fichier incorporé importé |

Les éléments `info` et `label` ne peuvent pas être obligatoires. Types inconnus et séparateurs incompatibles sont refusés. Les types notés, dépendances conditionnelles, pages multiples et échelles spécifiques ne sont pas fabriqués par ce profil.

```json
{"type":"feedback","idnumber":"avis","name":"Votre retour","intro":"<p>Un retour par personne.</p>","completion":"submit","anonymous":true,"items":[{"key":"utilite","type":"multichoice","name":"Ce parcours est-il utile ?","required":true,"choices":["Oui","À améliorer"]},{"key":"detail","type":"textarea","name":"Une suggestion","required":false}]}
```

**Anonymat :** c'est le mode natif de restitution des réponses. L'essai Moodle 5.1.8+ du 2026-11-01 a constaté `anonymous_response=1` tout en conservant un userid dans la table native. Ne pas promettre l'absence de lien en base ou dans les journaux ; définir les accès et l'usage des résultats dans le projet.

## Leçon

Activité `type: "lesson"`, non notée au carnet (`grade=0`, pratique). `completion` : `none`, `manual`, `view` ou **`end`**, qui exige d'atteindre la fin, pas seulement de consulter la première page. Pas de durée minimale imposée ni nouvelle tentative complète configurable.

`pages` : tableau ordonné. Chaque page contient `key` unique, `type` (`content` ou `question`), `title`, `html`, `choices`. Les sauts sont des clés logiques, jamais des identifiants source. **`END` est réservé à la fin** et ne peut pas nommer une page.

Chaque choix : `{text, to, response?, correct?}`. `to` est une clé existante ou `END` ; `response` est un texte de retour, vide par défaut ; `correct` booléen faux par défaut. Une page `content` exige au moins un bouton ; une page `question` est un choix multiple à réponse unique, au moins deux réponses et exactement une correcte. Scores internes 1/0 ; ils guident la Leçon mais ne constituent pas une évaluation finale au carnet.

La première page déclarée est le début ; l'ordre structurel et les sauts sont deux choses distinctes. Les pages sont créées d'abord, puis les sauts sont associés aux nouveaux identifiants. Le vérificateur suit la chaîne des pages et compare les destinations après restauration. Chaque page doit offrir un chemin vers END ; les retours volontaires restent possibles. Cela ne garantit pas que toutes les branches ont été parcourues par un apprenant.

```json
{"type":"lesson","idnumber":"parcours","name":"Vérifier un repère","intro":"<p>Aller jusqu’à la fin pour terminer.</p>","completion":"end","pages":[{"key":"debut","type":"content","title":"Découvrir","html":"<p>Prendre connaissance du repère.</p>","choices":[{"text":"Continuer","to":"verification"}]},{"key":"verification","type":"question","title":"Vérifier","html":"<p>Faut-il vérifier le résultat ?</p>","choices":[{"text":"Oui","to":"END","correct":true,"response":"Exact."},{"text":"Non","to":"debut","response":"Relire le repère."}]}]}
```

Hors profil : autres types de pages/questions, groupes, minuterie, médias incorporés, notation au carnet et tous les comportements de reprise. Une question de Leçon n'est pas une question de banque qbank.

## Attestation native

Activité `type: "customcert"` avec `certificate: {background, width?, height?}`. `background` est un PNG valide existant sous le projet ; largeur/hauteur en millimètres entiers, défaut 297 × 210, entre 50 et 1000. `condition` est l'idnumber d'une activité **déjà déclarée** en achèvement `pass`. `condition_state` : 1 par défaut, ou 2 explicite. `course_required: false` ; achèvement de l'attestation `none`, `manual` ou `view`.

```json
{"type":"customcert","idnumber":"attestation","name":"Attestation de réussite","intro":"<p>Accessible après réussite.</p>","completion":"view","course_required":false,"condition":"test-final","condition_state":1,"certificate":{"background":"certificat/fond.png","width":297,"height":210}}
```

Custom certificate doit être installé ; essai effectué avec **5.0.11**. Le module et son modèle/page sont créés par l'API d'activité native ; les éléments bgimage, studentname, date et code sont sérialisés par leur fabrique et enregistrés dans le schéma du plugin, avec événement de création. Le modèle appartient au contexte du module, **l'image au contexte du cours**. Une nouvelle zone d'image n'écrase pas les autres fonds du cours. Aucune émission ni donnée de destinataire reprise pour la fabrication.

Profil fixe : une page, fond pleine page, nom centré à mi-hauteur, date d'émission et code en dessous. Police freesans. Titres et décor peuvent figurer dans le fond préparé par le projet. Pas de signature, logo additionnel, positions/polices libres ou modèle complexe importé. Vérifier l'autorisation des éléments institutionnels et la lisibilité avec un nom long dans le projet concerné.

Le vérificateur compare format, éléments, positions, contexte et empreinte de l'image ; les deux états d'accès restent soumis aux deux comptes fictifs du [contrat principal](contrat-structure.md). L'émission et le PDF se vérifient séparément dans le navigateur. Le format de date suit la langue effective de la session ; un pack installé ne prouve pas son activation.

## Preuve et choix du moyen

**2026-11-01, Moodle 5.1.8+ local / Custom certificate 5.0.11 :** six modules construits, sauvegardés sans participants puis restaurés ; éléments, pages/sauts et fond vérifiés. Feedback incomplet refusé, complet accepté, deuxième réponse refusée, anonymat et achèvement natifs constatés. Parcours navigateur d'une branche de Leçon jusqu'à la fin et achèvement constaté. Deux étudiants fictifs ont échoué/réussi au test par API natives ; restriction et navigation de l'attestation refusées/autorisées ; PDF avec fond identique pixel pour pixel. La date restait en anglais ; ce point n'est pas annoncé résolu.

Pour un cours neuf dans une instance locale autorisée et ce profil simple, préférer cette construction native, puis la sauvegarde Moodle. Pour modifier une copie `.mbz` sans instance ou reprendre un modèle couvert plus riche (notamment image/signature), garder la [retouche depuis modèle](retouches-activites.md). Ne pas simplifier un modèle institutionnel pour le faire entrer dans le profil natif fixe. Les deux voies doivent être essayées après restauration dans leur propre portée.
