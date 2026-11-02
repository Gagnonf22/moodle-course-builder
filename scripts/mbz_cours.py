"""Découverte de métadonnées d'une copie extraite ; pas de restauration Moodle."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from mbz_archive import _write_atomic


def lire_xml(path):
    raw = Path(path).read_bytes()
    if len(raw) > 16 * 1024**2 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('XML trop grand ou avec DTD/entités non admises')
    root = ET.fromstring(raw)
    if root.tag.startswith('{'):
        raise ValueError('Ce profil de sauvegarde XML ne gère pas les espaces de noms')
    return root


def ecrire_xml(path, root):
    # Le détecteur de format Moodle cherche littéralement ces guillemets doubles
    # dans les 200 premiers octets de moodle_backup.xml, avant toute analyse XML.
    header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    _write_atomic(Path(path), header + ET.tostring(root, encoding='utf-8', xml_declaration=False) + b'\n')


def entier(value, *, zero=False):
    if not isinstance(value, str) or not re.fullmatch('[0-9]+', value) or int(value) < (0 if zero else 1):
        raise ValueError('Identifiant ou numéro absent/invalide')
    return int(value)


def champ(root, nom, valeur):
    node = root.find(nom)
    if node is None:
        raise ValueError(f'Champ XML requis absent : {nom}')
    node.text = str(valeur)


def nom_fichier(value):
    if (not isinstance(value, str) or not value or value in {'.', '..'} or
            any(c in value for c in '/\\:') or any(ord(c) < 32 for c in value)):
        raise ValueError('Nom de fichier simple requis')
    return value


class Cours:
    def __init__(self, dossier, *, verifier_dependances=True):
        self.root = Path(dossier)
        self.xml = {p.relative_to(self.root).as_posix(): lire_xml(p)
                    for p in sorted(self.root.rglob('*.xml'))}
        self.backup = self.xml.get('moodle_backup.xml')
        self.files = self.xml.get('files.xml')
        if self.backup is None or self.files is None:
            raise ValueError('moodle_backup.xml et files.xml requis')
        self.sections, self.modules, self.ids = {}, {}, set()
        for tree in self.xml.values():
            for el in tree.iter():
                values = [v for k, v in el.attrib.items() if k.lower().endswith('id')]
                if el.tag.lower().endswith('id'):
                    values.append(el.text or '')
                for v in values:
                    if re.fullmatch('[0-9]+', v) and int(v) > 0:
                        self.ids.add(int(v))
        for path, tree in self.xml.items():
            if re.fullmatch(r'sections/[^/]+/section.xml', path):
                sid = entier(tree.get('id'))
                if sid in self.sections:
                    raise ValueError('Identifiant de section dupliqué')
                seq = tree.findtext('sequence') or ''
                sequence = [entier(s) for s in seq.split(',')] if seq else []
                if len(sequence) != len(set(sequence)):
                    raise ValueError('Module dupliqué dans une séquence')
                self.sections[sid] = dict(id=sid, numero=entier(tree.findtext('number'), zero=True),
                                          nom=tree.findtext('name') or '', sequence=sequence, tree=tree, path=path)
            if re.fullmatch(r'activities/[^/]+/module.xml', path):
                mid = entier(tree.get('id'))
                kind = tree.findtext('modulename')
                if not isinstance(kind, str) or not re.fullmatch('[a-z][a-z0-9_]*', kind):
                    raise ValueError('Type de module invalide')
                directory = f'activities/{kind}_{mid}'
                if path != directory + '/module.xml' or mid in self.modules:
                    raise ValueError('Identifiant/dossier de module incohérent ou dupliqué')
                detail = self.xml.get(directory + f'/{kind}.xml')
                obj = detail.find(kind) if detail is not None else None
                self.modules[mid] = dict(id=mid, type=kind, idnumber=tree.findtext('idnumber') or '',
                                        nom=obj.findtext('name') or '' if obj is not None else '',
                                        section=entier(tree.findtext('sectionid')), tree=tree,
                                        path=path, directory=directory, detail=detail)
        if not self.sections or not self.modules:
            raise ValueError('Sections et modules de cours requis')
        assigned = []
        for sec in self.sections.values():
            for mid in sec['sequence']:
                if mid not in self.modules or self.modules[mid]['section'] != sec['id']:
                    raise ValueError('Séquence et section du module incohérentes ou export partiel')
                if self.modules[mid]['tree'].findtext('sectionnumber') != str(sec['numero']):
                    raise ValueError('Numéro de section incohérent')
                assigned.append(mid)
        if len(assigned) != len(set(assigned)) or set(assigned) != self.modules.keys():
            raise ValueError('Chaque module doit figurer dans sa section, une seule fois')
        if verifier_dependances:
            def verifier(value):
                if isinstance(value, dict):
                    if value.get('type') == 'completion':
                        mid = value.get('cm')
                        if type(mid) is not int or mid not in self.modules:
                            raise ValueError('Restriction d’achèvement vers un module absent')
                    for child in value.values():
                        verifier(child)
                elif isinstance(value, list):
                    for child in value:
                        verifier(child)
            for tree in self.xml.values():
                for el in tree.iter():
                    if el.tag in {'availability', 'availabilityjson'} and el.text not in (None, '', '$@NULL@$'):
                        verifier(json.loads(el.text))
        self.file_rows = {}
        for row in self.files.findall('file'):
            fid = entier(row.get('id'))
            if fid in self.file_rows:
                raise ValueError('Identifiant de fichier dupliqué')
            self.file_rows[fid] = row

    def nouveau_id(self):
        value = max(self.ids, default=0) + 1
        if value > 2147483647:
            raise ValueError('Domaine d’identifiants trop grand pour ce profil')
        self.ids.add(value)
        return value

    def choisir(self, selector, *, section=False):
        allowed = {'id', 'numero', 'nom'} if section else {'id', 'nom', 'idnumber', 'type'}
        if not isinstance(selector, dict) or not selector or selector.keys() - allowed:
            raise ValueError('Sélecteur explicite invalide')
        for key, value in selector.items():
            if key in {'id', 'numero'}:
                if type(value) is not int or value < (0 if key == 'numero' else 1):
                    raise ValueError('Sélecteur numérique invalide')
            elif not isinstance(value, str) or not value:
                raise ValueError('Sélecteur textuel non vide requis')
        rows = self.sections.values() if section else self.modules.values()
        matches = [r for r in rows if all(r[k] == v for k, v in selector.items())]
        if len(matches) != 1:
            raise ValueError(f'Sélecteur absent ou ambigu : {len(matches)} correspondances')
        return matches[0]

    def blob(self, row):
        sha = row.findtext('contenthash') or ''
        if not re.fullmatch('[0-9a-f]{40}', sha):
            raise ValueError('Empreinte de fichier invalide')
        path = self.root / 'files' / sha[:2] / sha
        if not path.is_file():
            raise ValueError('Fichier référencé non intégré ; dépôt externe non géré')
        h = hashlib.sha1()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        if h.hexdigest() != sha or row.findtext('filesize') != str(path.stat().st_size):
            raise ValueError('Blob de fichier incohérent')
        return path

    def enregistrer(self, paths):
        for path in sorted(set(paths)):
            ecrire_xml(self.root / path, self.xml[path])
