# Sections, ressources et navigation

**Moyen :** interface Moodle ou fonctions autorisées réellement disponibles. Le constructeur PHP inclus couvre H5P/Page/Fichier et, avec le [contrat v2](contrat-structure.md), Livre avec chapitres HTML et sous-chapitres. Il ne fabrique pas URL ou Dossier. Les médias de chapitre ne sont pas importés par ce profil.

## Préparer la structure

Relever pour chaque objet : clé stable de projet, nom, section, contenu ou fichier source, visibilité, chemin d'accès prévu et achèvement souhaité. Distinguer section d'accueil, sections de travail et éventuelles ressources communes. Choisir le format du cours selon la navigation voulue et les composants du site ; un export `tiles` ou `recit` n'assure pas que ce format sera disponible ailleurs.

Créer ou repérer les sections dans le cours autorisé. En faire la page principale selon [Concevoir une section](concevoir-section.md) : contenu riche et propre à chaque étape, objectifs, points clés, médias intégrés, consigne et coche expliquée avant chaque activité requise. Créer les ressources en conservant leurs sources éditables ; relever les identifiants retournés seulement dans le projet. Après enregistrement, rouvrir les contenus pour détecter les transformations de l'éditeur et les liens rompus.

| Objet | Contenu à préparer | Contrôle utile |
|---|---|---|
| Zone de texte et média / résumé de section | Page principale : bandeau, objectifs, points clés, consignes, intégrations | La section reste lisible et les liens mènent à des objets accessibles |
| Page | Longue lecture justifiant de quitter la section, médias et textes alternatifs | Images enregistrées dans la bonne zone de fichiers ; rendu après réouverture |
| Livre | Rarement : longue référence en plusieurs chapitres ; justifier la navigation ajoutée | Sommaire, précédent/suivant, médias de chaque chapitre |
| Fichier | Document à télécharger/utiliser, Word ou PDF mis en forme ; jamais .txt sauf licence | Téléchargement possible, document lisible ; alternative si le format est inaccessible |
| Dossier | Ensemble utile de fichiers organisés | Aucun fichier essentiel enfoui sans explication |
| URL | Adresse, titre, rôle de la ressource, solution de repli si nécessaire | Accès sous le rôle prévu ; authentification et pérennité ne sont pas présumées |

## Visibilité et dépendances

Ne pas confondre activité masquée et activité disponible sans affichage dans la page du cours. Dans le deuxième cas, fournir un lien ou une intégration permettant réellement de l'atteindre ; vérifier cette distinction avec un compte apprenant. Le mode dépend de la configuration du site et des possibilités du format. [Moodle : activités furtives](https://docs.moodle.org/501/en/Stealth_activities).

Pour déplacer ou dupliquer une activité, vérifier la séquence de section, les liens entrants, restrictions et conditions d'achèvement. Une copie de HTML ne transporte pas à elle seule les fichiers ni les références Moodle.

Ajouter un bloc de progression, de résultats ou de badges seulement s'il facilite une action ou une lecture attendue. Les blocs et badges ne se déduisent pas du seul compteur de modules d'une sauvegarde. Contrôler leur configuration et leur visibilité séparément.

## Résultat attendu

Le plan et le cours concordent ; chaque ressource est atteignable sous le rôle prévu, ses médias sont présents ou leurs dépendances documentées, et l'achèvement correspond à une action vérifiable. Une belle page d'accueil ne prouve pas la navigation.

**Sources :** [ressources Moodle](https://docs.moodle.org/501/en/Resources) ; modèles de navigation et dépendances observés hors ligne. Livre éprouvé le 2026-11-01 sur Moodle 5.1.8+ local : construction, sauvegarde/restauration, contenu et consultation des deux chapitres ; les autres moyens et médias restent à essayer selon le site cible.
