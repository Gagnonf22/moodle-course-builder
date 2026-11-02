"""Écritures de nouveaux livrables sans écraser les fichiers existants."""
import os
from pathlib import Path
import tempfile


def publier_nouveau(temporaire, destination):
    """Publier par réservation exclusive puis remplacement de notre réservation.

    Le temporaire doit être complet et sur le même volume que la destination.
    Une réservation vide peut être visible pendant cette opération. Ce n'est
    pas un verrou contre un autre programme qui modifie volontairement ce nom.
    """
    destination = Path(destination)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    identity = os.fstat(fd)
    os.close(fd)
    try:
        os.replace(temporaire, destination)
    except BaseException:
        # Ne pas effacer un fichier que quelqu'un aurait remplacé entretemps.
        try:
            current = destination.stat()
            if (current.st_dev, current.st_ino, current.st_size) == (identity.st_dev, identity.st_ino, 0):
                destination.unlink()
        except FileNotFoundError:
            pass
        raise


def ecrire_nouveau(destination, content):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.mcb-', dir=destination.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
        publier_nouveau(name, destination)
    finally:
        Path(name).unlink(missing_ok=True)


def chemin_projet(projet, relatif):
    """Résoudre un média relatif au projet, sans sortir de sa racine."""
    root = Path(projet).resolve()
    relative = Path(relatif)
    if relative.is_absolute() or relative.drive:
        raise ValueError('Un chemin de média doit être relatif au projet')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Le chemin sort du projet')
    if not path.is_file():
        raise FileNotFoundError(f'Média absent : {relative}')
    return path
