# Socle de retouche et scripts CLI — développement en cours

**Version de travail :** socle de 2b complété en 3a le 2026-11-01. Avant tout usage réel des scripts PHP ci-dessous, appliquer les préconditions d'[automatisation.md](automatisation.md). Les exemples CLI ne constituent pas une autorisation ni une validation en instance.

## Extraction et réemballage hors ligne

Lire ce document pour utiliser `scripts/mbz_archive.py`. Python 3.13 ou ultérieur ; bibliothèque standard uniquement. Les tests du développement actuel ont été exécutés sous Python 3.14. Les autres versions compatibles déclarées restent à essayer.

- Travailler sur une copie, dans un dossier temporaire court. Ne pas extraire les sauvegardes sous une arborescence OneDrive profonde.
- Après extraction, le déplacement du staging reprend au plus six fois les seuls refus Windows `WinError 5/32/33`, avec pauses bornées (0,31 s au total). Une destination réapparue, un lien, une autre erreur ou un refus persistant interrompt ; aucune suppression récursive ni écrasement. Intermittence constatée lors des essais, cause externe non attribuée.
- `extraire(src, dossier)` accepte une archive TAR/gzip vers une destination vide. Précontrôle des chemins, liens, doublons et plafonds (100 000 entrées, 8 Gio déclarés, ajustables), puis extraction en staging. Le staging est créé à côté de la destination : choisir un parent court.
- `remplacer(chemin, ancien, nouveau, compte=1)` exige exactement le nombre attendu de motifs. Une absence ou une ambiguïté interrompt sans modifier le fichier. Cette exigence est plus stricte que celle du prototype ; vérifier ses appelants lors de la reprise des retouches.
- `reemballer(dossier, dst)` vérifie la syntaxe XML, régénère `.ARCHIVE_INDEX` en première entrée et utilise USTAR sans en-têtes PAX. L'index du dossier source reste intact. La sortie doit être nouvelle et hors du dossier source.
- La publication utilise une réservation exclusive de la sortie puis remplace cette réservation par le temporaire complet, sur le même volume. Une réservation vide peut être visible brièvement ; elle est nettoyée en cas d'exception ordinaire. Aucun lien physique n'est requis. Ce mécanisme ne protège pas d'un arrêt brutal ni d'un programme concurrent qui remplace volontairement la réservation.
- `remplacer` travaille sur les octets UTF-8 : les CRLF, LF mixtes et BOM hors motif restent inchangés. Les nouveaux fichiers JSON/VTT sont écrits explicitement en LF ; les médias déjà relus sont copiés sans conversion.

Exemple, à exécuter dans un environnement de travail autorisé :

```python
import tempfile
from pathlib import Path
from mbz_archive import extraire, reemballer

with tempfile.TemporaryDirectory(prefix='mbz-') as work:
    dest = Path(work) / 'contenu'
    extraire('entree.mbz', dest)
    # Appliquer ici une retouche explicite à la copie extraite.
    reemballer(dest, 'sortie-nouvelle.mbz')
```

Les tests synthétiques vérifient des invariants de format et des refus. Le contrôle hors ligne d'une archive réelle vérifie la conservation de ses fichiers ; ni l'un ni l'autre ne démontre la restauration Moodle. Les limites de ressources ne constituent pas une isolation complète d'un fichier hostile.

## Scripts PHP issus du prototype

Trois commandes et leur garde-fou partagé sont présents sous `scripts/moodle/`. Le constructeur conserve son profil H5P/Page/Fichier ; le vérificateur étendu couvre aussi attestation et rétroaction, selon le contrat lié ci-dessous. Les API H5P/Page/Fichier/attestation et la sauvegarde ont été éprouvées dans Moodle 5.1.8+ local (2026-11-01) ; les autres familles restent à essayer.

- `construire_cours.php` : création masquée d'un cours neuf selon `cours/structure.json`. Exige `--validation-locale`, un `$CFG->wwwroot` en boucle locale et un `dbhost` explicite parmi `localhost`, `127.0.0.1`, `::1`, `[::1]`. Base distante, absente ou invalide refusée avant l'élévation et les actions de construction. Le socket Unix se configure par `dboptions['dbsocket']` (booléen ou chemin Unix absolu local) avec `dbhost=localhost` ; les chemins réseau/relatifs sont refusés. Refuse un nom abrégé existant ; aucune suppression automatique.
- Ces contrôles interviennent **après le chargement de `config.php`** : ils n'isolent pas ses effets de bootstrap, un tunnel local ou des options avancées de connexion. Fournir une instance, base et fichiers locaux réellement isolés et autorisés ; une instance persistante d’essai doit avoir un état propre de secours et rester arrêtée hors usage. La configuration de socket suit [config-dist.php de Moodle 5.1](https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/config-dist.php) ; les tests unitaires ne se connectent à aucune base ; M1 a utilisé séparément une base locale réelle en TCP, pas un socket Unix.
- `verifier_cours.php` : contrôle de structure, fichiers, notes et réglages d'achèvement ; sortie 0 si aucun échec, 1 si des contrôles échouent. Ce script ne vérifie pas le parcours réel d'un étudiant ni le PDF d'une attestation.
- Le champ facultatif `author` de la spécification remplace l'auteur institutionnel du prototype ; sa valeur par défaut est vide. La licence de fichier reste celle du prototype (`allrightsreserved`), à rendre configurable lors de la généralisation.

```text
php construire_cours.php --moodle=<instance-locale> --projet=<projet> --validation-locale
php verifier_cours.php --validation-locale --moodle=<instance-locale> --courseid=<id> --projet=<projet>
```

Les tests PHP utilisent une doublure minimale de Moodle, sans base de données. Ils exécutent les scripts réels pour contrôler les branches de refus, l'expression d'achèvement et le code de sortie. Ils ne valident pas les API Moodle. Définir `PHP_BIN` si PHP CLI n'est pas dans le PATH ; les tests sont signalés comme ignorés si PHP est absent.

```text
python -B -m unittest discover -s tests -v
```

Pour le contrat étendu et les deux états d’attestation, lire [contrat-structure.md](contrat-structure.md). Le sauvegardeur natif et ses limites sont décrits dans [automatisation.md](automatisation.md).
