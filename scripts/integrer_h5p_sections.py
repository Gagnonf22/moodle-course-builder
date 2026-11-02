"""Intégrer les H5P existants d'une copie TAR/gzip ; aucun accès à Moodle."""
import argparse
import json
from pathlib import Path
import tempfile
from urllib.parse import quote

from mbz_archive import extraire, reemballer
from mbz_cours import Cours, entier, champ, nom_fichier


def integrer(src, dst, *, modules=None, ancre=None):
    if Path(dst).exists():
        raise FileExistsError('Sortie existante refusée')
    if ancre is not None and (not isinstance(ancre, str) or not ancre):
        raise ValueError('Ancre HTML non vide requise')
    with tempfile.TemporaryDirectory(prefix='mbzi-') as tmp:
        dossier = Path(tmp) / 'cours'
        extraire(src, dossier)
        cours = Cours(dossier)
        if modules is not None:
            if (not isinstance(modules, list) or not modules or
                    any(type(m) is not int or m <= 0 for m in modules) or len(set(modules)) != len(modules)):
                raise ValueError('Liste de modules numériques uniques requise')
            if any(m not in cours.modules for m in modules):
                raise ValueError('Module demandé absent')
            chosen = [cours.modules[m] for m in modules]
        else:
            chosen = [m for m in cours.modules.values() if m['type'] == 'h5pactivity']
        if not chosen or any(m['type'] != 'h5pactivity' for m in chosen):
            raise ValueError('Au moins une activité h5pactivity est requise')
        grouped, changed, report = {}, [], []
        for mod in chosen:
            detail = mod['detail']
            if detail is None or detail.get('modulename') != 'h5pactivity' or detail.get('moduleid') != str(mod['id']):
                raise ValueError('Métadonnées de l’activité H5P incohérentes')
            ctx = entier(detail.get('contextid'))
            if mod['tree'].findtext('visible') != '1' or mod['tree'].findtext('visibleoncoursepage') != '1':
                raise ValueError('Activité H5P déjà furtive ou indisponible ; retouche refusée')
            if mod['tree'].findtext('availability') not in (None, '', '$@NULL@$'):
                raise ValueError('Restrictions d’activité à préserver : intégration non automatique dans ce profil')
            rows = [f for f in cours.file_rows.values() if f.findtext('component') == 'mod_h5pactivity'
                    and f.findtext('filearea') == 'package' and f.findtext('contextid') == str(ctx)
                    and f.findtext('filename') != '.']
            if len(rows) != 1:
                raise ValueError('Paquet H5P absent ou ambigu dans files.xml')
            row = rows[0]
            if row.findtext('itemid') != '0' or row.findtext('filepath') != '/':
                raise ValueError('Zone de paquet H5P non gérée')
            filename = nom_fichier(row.findtext('filename'))
            if not filename.lower().endswith('.h5p'):
                raise ValueError('Extension de paquet H5P requise')
            cours.blob(row)
            marker = ('<div class="h5p-placeholder mt-3 mb-3" contenteditable="false">'
                      f'$@PLUGINFILEBYCONTEXT*{ctx}@$/mod_h5pactivity/package/0/{quote(filename, safe="")}'
                      '?component=mod_h5pactivity</div>')
            grouped.setdefault(mod['section'], {})[mod['id']] = marker
            report.append(dict(module=mod['id'], section=mod['section'], contexte=ctx, fichier=filename))
            champ(mod['tree'], 'visibleoncoursepage', 0)
            changed.append(mod['path'])
        for sid, markers in grouped.items():
            sec = cours.sections[sid]
            if sec['tree'].findtext('visible') != '1':
                raise ValueError('Section masquée : intégration automatique refusée')
            if sec['tree'].findtext('summaryformat') != '1':
                raise ValueError('Résumé de section HTML requis')
            summary = sec['tree'].findtext('summary') or ''
            if 'h5p-placeholder' in summary or '/mod_h5pactivity/package/' in summary:
                raise ValueError('Section contenant déjà une intégration : double application refusée')
            html = ''.join(markers[m] for m in sec['sequence'] if m in markers)
            if ancre is None:
                updated = summary + html
            else:
                if summary.count(ancre) != 1:
                    raise ValueError('Ancre HTML absente ou ambiguë dans une section ciblée')
                updated = summary.replace(ancre, html + ancre, 1)
            champ(sec['tree'], 'summary', updated)
            changed.append(sec['path'])
        cours.enregistrer(changed)
        reemballer(dossier, dst)
        return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('sortie')
    p.add_argument('--modules', nargs='+', type=int, help='Identifiants dans cette sauvegarde ; tous les H5P par défaut')
    p.add_argument('--ancre', help='Texte HTML exact avant lequel insérer ; fin de résumé par défaut')
    a = p.parse_args()
    print(json.dumps(integrer(a.source, a.sortie, modules=a.modules, ancre=a.ancre), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
