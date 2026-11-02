"""Créer des copies MP4 pour H5P, sans remplacer les originaux ou une sortie."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from fichiers import publier_nouveau


def trouver_ffmpeg(chemin=None):
    candidate = chemin or os.environ.get('FFMPEG_EXE') or shutil.which('ffmpeg')
    resolved = shutil.which(str(candidate)) if candidate else None
    if not resolved:
        raise FileNotFoundError('FFmpeg absent : fournir --ffmpeg ou FFMPEG_EXE')
    return resolved


def encoder(source, destination, *, ffmpeg=None, debut=None, fin=None,
            crf=30, fps=15, preset='slow', audio_kbps=64):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise FileNotFoundError('Vidéo source absente')
    if source == destination or destination.exists():
        raise FileExistsError('La sortie doit être nouvelle et différente de la source')
    if debut is not None and debut < 0 or fin is not None and fin <= (debut or 0):
        raise ValueError('Intervalle de découpe invalide')
    if not 0 <= crf <= 51 or fps <= 0 or audio_kbps <= 0:
        raise ValueError('Réglages d’encodage invalides')
    ffmpeg = trouver_ffmpeg(ffmpeg)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.mcb-', suffix='.mp4', dir=destination.parent)
    os.close(fd)
    cut = (['-ss', str(debut)] if debut is not None else []) + (['-to', str(fin)] if fin is not None else [])
    # Aucun agrandissement : seules les vidéos dépassant 1080p sont réduites.
    scale = "scale=w='min(1920,iw)':h='min(1080,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2"
    command = [ffmpeg, '-v', 'error', '-y', '-i', str(source), *cut,
               '-map', '0:v:0', '-map', '0:a:0?', '-vf', scale,
               '-c:v', 'libx264', '-preset', preset, '-tune', 'stillimage', '-crf', str(crf),
               '-r', str(fps), '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
               '-c:a', 'aac', '-b:a', f'{audio_kbps}k', '-ac', '1', '-dn', '-map_metadata', '-1', temporary]
    try:
        subprocess.run(command, check=True)
        if not Path(temporary).stat().st_size:
            raise ValueError('FFmpeg a produit un fichier vide')
        publier_nouveau(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs='+')
    parser.add_argument('--sortie', required=True)
    parser.add_argument('--ffmpeg')
    parser.add_argument('--debut', type=float)
    parser.add_argument('--fin', type=float)
    parser.add_argument('--nom')
    parser.add_argument('--crf', type=int, default=30)
    parser.add_argument('--fps', type=float, default=15)
    parser.add_argument('--preset', default='slow')
    parser.add_argument('--audio-kbps', type=int, default=64)
    args = parser.parse_args()
    if args.nom and (len(args.sources) != 1 or Path(args.nom).name != args.nom or '/' in args.nom or '\\' in args.nom):
        parser.error('--nom est un nom simple réservé à une source unique')
    targets = [Path(args.sortie) / ((args.nom or Path(src).stem) + '.mp4') for src in args.sources]
    if len({str(p.resolve()).casefold() for p in targets}) != len(targets):
        parser.error('Plusieurs sources ont le même nom de sortie')
    for src, dst in zip(args.sources, targets):
        encoder(src, dst, ffmpeg=args.ffmpeg, debut=args.debut, fin=args.fin,
                crf=args.crf, fps=args.fps, preset=args.preset, audio_kbps=args.audio_kbps)
        print(f'{dst.name}: {dst.stat().st_size} octets')


if __name__ == '__main__':
    main()
