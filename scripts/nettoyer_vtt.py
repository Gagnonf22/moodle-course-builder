"""Nettoyer un WebVTT simple ; corrections du projet fournies par JSON.

Les phrases suspectes ne sont supprimées qu'avec une option explicite.
Les sous-titres doivent toujours être relus avec la vidéo.
"""
import argparse
import json
from pathlib import Path
import re

from fichiers import ecrire_nouveau

HALLUCINATIONS = re.compile(r"^(merci( d'avoir regardé cette vidéo)?\s*!?\.?|sous-titrage)$", re.I)
TIME = r'(?:\d{2,}:)?\d{2}:\d{2}\.\d{3}'
TIMING = re.compile(rf'^({TIME})\s+-->\s+({TIME})(.*)$')


def secondes(value):
    parts = value.split(':')
    if len(parts) == 2:
        parts.insert(0, '0')
    h, m, s = parts
    if not 0 <= int(m) < 60 or not 0 <= float(s) < 60:
        raise ValueError('Horodatage WebVTT invalide')
    return int(h) * 3600 + int(m) * 60 + float(s)


def horodatage(value):
    millis = round(value * 1000)
    h, rest = divmod(millis, 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}.{ms:03d}'


def lignes(text, largeur=42):
    result, current = [], ''
    for word in filter(None, text.split(' ')):
        if current and len(current) + 1 + len(word) > largeur:
            result.append(current)
            current = word
        else:
            current = f'{current} {word}'.strip()
    return result + ([current] if current else [])


def charger_corrections(path):
    if path is None:
        return []
    corrections = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(corrections, list) or any(not isinstance(pair, list) or len(pair) != 2
            or not all(isinstance(v, str) for v in pair) or not pair[0] for pair in corrections):
        raise ValueError('Corrections attendues : [["ancien", "nouveau"], ...]')
    return corrections


def nettoyer(source, destination, *, corrections=None, largeur=42, nombre_lignes=2,
             retirer_hallucinations=False):
    if largeur < 1 or nombre_lignes < 1:
        raise ValueError('Largeur et nombre de lignes doivent être positifs')
    text = Path(source).read_text(encoding='utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    blocks = re.split(r'\n\s*\n', text.strip())
    if not blocks or not re.fullmatch(r'WEBVTT(?:[ \t].*)?', blocks[0]):
        raise ValueError('En-tête WEBVTT requis, sans métadonnées non prises en charge')
    output = ['WEBVTT', '']
    count, removed, previous_start = 0, 0, -1
    for block in blocks[1:]:
        rows = block.split('\n')
        if rows[0] == 'NOTE' or rows[0].startswith(('NOTE ', 'NOTE\t')):
            output.extend([block, ''])
            continue
        # Refuser les constructions non gérées, plutôt que perdre du contenu.
        index = 0 if '-->' in rows[0] else 1
        match = TIMING.fullmatch(rows[index]) if index < len(rows) else None
        if not match or len(rows) <= index + 1:
            raise ValueError('Réplique ou bloc WebVTT non pris en charge')
        start, end = secondes(match[1]), secondes(match[2])
        if end <= start or start < previous_start:
            raise ValueError('Intervalle de sous-titre invalide ou désordonné')
        previous_start = start
        content = ' '.join(' '.join(rows[index+1:]).split())
        if retirer_hallucinations and HALLUCINATIONS.fullmatch(content):
            removed += 1
            continue
        for old, new in corrections or []:
            content = content.replace(old, new)
        content = content.replace('« ', '«\u00a0').replace(' »', '\u00a0»')
        wrapped = lignes(content, largeur)
        groups = [wrapped[i:i+nombre_lignes] for i in range(0, len(wrapped), nombre_lignes)]
        total = sum(len(' '.join(g)) for g in groups)
        if not total:
            raise ValueError('Une correction a vidé une réplique')
        elapsed = 0
        for i, group in enumerate(groups):
            begin = start + (end-start) * elapsed / total
            elapsed += len(' '.join(group))
            finish = end if i == len(groups)-1 else start + (end-start) * elapsed / total
            if round(begin*1000) >= round(finish*1000):
                raise ValueError('Découpage trop fin pour la durée disponible')
            count += 1
            output.extend([str(count), f'{horodatage(begin)} --> {horodatage(finish)}{match[3]}', '\n'.join(group), ''])
    if not count:
        raise ValueError('Aucune réplique conservée')
    ecrire_nouveau(destination, ('\n'.join(output) + '\n').encode('utf-8'))
    return {'repliques': count, 'supprimees': removed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('destination')
    parser.add_argument('--corrections', help='JSON de corrections fourni par le projet')
    parser.add_argument('--largeur', type=int, default=42)
    parser.add_argument('--lignes', type=int, default=2)
    parser.add_argument('--retirer-hallucinations', action='store_true')
    args = parser.parse_args()
    print(nettoyer(args.source, args.destination, corrections=charger_corrections(args.corrections),
                   largeur=args.largeur, nombre_lignes=args.lignes,
                   retirer_hallucinations=args.retirer_hallucinations))


if __name__ == '__main__':
    main()
