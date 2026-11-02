"""Retouches TAR/gzip Moodle : index en tête, USTAR, écritures transactionnelles.

Utiliser un dossier temporaire court pour l'extraction sous Windows.
La validité XML et la structure TAR ne prouvent pas la restaurabilité Moodle.
"""
import io
import ntpath
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import tarfile
import tempfile
import time
import xml.etree.ElementTree as ET

from fichiers import publier_nouveau


def _publier_dossier(stage, destination):
    """Reprise bornée des refus Windows transitoires, sans écraser de dossier."""
    for tentative in range(6):
        if Path(destination).exists() or Path(destination).is_symlink():
            raise FileExistsError('Destination de staging déjà présente')
        try:
            Path(stage).rename(destination)
            return
        except PermissionError as erreur:
            if (getattr(erreur, 'winerror', None) not in {5, 32, 33} or tentative == 5
                    or Path(destination).exists() or Path(destination).is_symlink()):
                raise
            time.sleep(0.01 * 2**tentative)


def extraire(src, dossier, *, max_entries=100000, max_bytes=8 * 1024**3):
    """Extraire dans une destination vide ; refuser liens et chemins ambigus.

    Précontrôle complet puis extraction en staging : aucun fichier partiel dans
    la destination si l'archive est invalide. Les plafonds sont ajustables.
    """
    src, dest = Path(src).resolve(), Path(dossier).absolute()
    if dest.is_symlink() or (dest.exists() and (not dest.is_dir() or any(dest.iterdir()))):
        raise ValueError('La destination doit être un dossier vide, sans lien')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(src, 'r:gz') as archive:
        members, seen, total = [], set(), 0
        for member in archive:
            name = member.name
            parts = PurePosixPath(name).parts
            if (not name or '\\' in name or ':' in name or '\n' in name or '\r' in name
                    or '\t' in name or PurePosixPath(name).is_absolute()
                    or PureWindowsPath(name).drive or '..' in parts
                    or not (member.isfile() or member.isdir())):
                raise ValueError(f'Entrée TAR refusée : {name!r}')
            # Windows normalise notamment la casse, les points et espaces finaux.
            if any(ntpath.isreserved(p) for p in parts):
                raise ValueError(f'Nom non portable : {name!r}')
            key = '/'.join(parts).casefold()
            if not key or key in seen:
                raise ValueError(f'Entrée TAR vide ou dupliquée : {name!r}')
            seen.add(key)
            members.append(member)
            total += member.size
            if len(members) > max_entries or total > max_bytes:
                raise ValueError('Limite de taille ou de nombre d’entrées dépassée')
        with tempfile.TemporaryDirectory(prefix='mbz-', dir=dest.parent) as stage:
            archive.extractall(stage, members=members, filter='data')
            if dest.exists():
                dest.rmdir()  # vide ; pas de suppression récursive
            _publier_dossier(stage, dest)
            # TemporaryDirectory tolère la disparition du dossier de staging.


def remplacer(chemin, ancien, nouveau, compte=1):
    """Remplacer un nombre exact de motifs, sans modification si ambigu."""
    path = Path(chemin)
    content = path.read_bytes()
    ancien, nouveau = ancien.encode('utf-8'), nouveau.encode('utf-8')
    if not ancien or compte < 1 or content.count(ancien) != compte:
        raise ValueError(f'Motif absent ou ambigu dans {path.name} (attendu : {compte})')
    updated = content.replace(ancien, nouveau, compte)
    _write_atomic(path, updated)


def _write_atomic(path, content):
    fd, tmp = tempfile.mkstemp(prefix='.mbz-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def reemballer(dossier, dst):
    """Valider les XML et produire une nouvelle archive, sans écraser de fichier.

    L'index est construit en mémoire ; le dossier source reste intact. Une
    erreur de validation ou de format USTAR ne laisse aucun livrable partiel.
    """
    source, output = Path(dossier).resolve(), Path(dst).absolute()
    if not source.is_dir():
        raise ValueError('Dossier source absent')
    if output.exists() or output.is_symlink():
        raise FileExistsError('La sortie existe déjà ; choisir un nouveau chemin')
    if output.resolve().is_relative_to(source):
        raise ValueError('La sortie doit être hors du dossier à archiver')
    entries = []
    for current, dirs, files in os.walk(source, followlinks=False):
        dirs.sort()
        files.sort()
        for name in dirs + files:
            item = Path(current) / name
            if item.is_symlink() or not (item.is_dir() or item.is_file()):
                raise ValueError('Liens et fichiers spéciaux refusés')
        relative = Path(current).relative_to(source).as_posix()
        if relative != '.':
            entries.append((relative, True))
        for name in files:
            item = Path(current) / name
            rel = item.relative_to(source).as_posix()
            if rel == '.ARCHIVE_INDEX':
                continue
            if item.suffix.lower() == '.xml':
                ET.parse(item)
            entries.append((rel, False))
    now = int(time.time())
    lines = [f'Moodle archive file index. Count: {len(entries)}']
    for rel, directory in entries:
        if any(c in rel for c in '\t\r\n'):
            raise ValueError('Nom incompatible avec l’index Moodle')
        lines.append(f'{rel}/\td\t0\t?' if directory else
                     f'{rel}\tf\t{(source / rel).stat().st_size}\t{now}')
    index = ('\n'.join(lines) + '\n').encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.mbz-', dir=output.parent)
    os.close(fd)

    def ustar(info):
        info.mtime = int(info.mtime)
        info.uid, info.gid, info.uname, info.gname = 0, 0, '', ''
        return info

    try:
        with tarfile.open(tmp, 'w:gz', format=tarfile.USTAR_FORMAT) as archive:
            info = tarfile.TarInfo('.ARCHIVE_INDEX')
            info.size, info.mtime = len(index), now
            archive.addfile(info, io.BytesIO(index))
            for rel, _ in entries:
                archive.add(source / rel, arcname=rel, recursive=False, filter=ustar)
        publier_nouveau(tmp, output)
    finally:
        Path(tmp).unlink(missing_ok=True)
