#!/usr/bin/env python3
"""Inventaire structurel hors ligne d’une sauvegarde Moodle, en lecture seule, sans extraction."""
import argparse, collections, json, os, tarfile, xml.etree.ElementTree as ET

def main():
    p=argparse.ArgumentParser(description=__doc__, add_help=False)
    p.add_argument('-h','--help','--aide',action='help',help='Afficher cette aide et quitter.')
    p.add_argument_group('arguments').add_argument('backup',metavar='SAUVEGARDE',help='Sauvegarde Moodle TAR à examiner.')
    p.add_argument('--sortie','--output',dest='output',metavar='FICHIER',help='Fichier JSON neuf ; affichage à l’écran par défaut.')
    a=p.parse_args()
    if not tarfile.is_tarfile(a.backup): raise SystemExit('Archive non prise en charge : format TAR attendu')
    with tarfile.open(a.backup,'r:*') as tf:
        members=tf.getmembers()
        if len(members)>100000: raise SystemExit('Trop de membres dans l’archive')
        if any(m.issym() or m.islnk() or m.name.startswith('/') or '..' in m.name.split('/') for m in members):raise SystemExit('Nom ou type de membre non sûr')
        if sum(m.size for m in members)>8*1024**3: raise SystemExit('La taille décompressée dépasse la limite d’inspection')
        normalized={}
        for m in members:
            name=m.name
            while name.startswith('./'):name=name[2:]
            if name in ('','.') and m.isdir():continue
            if name in normalized:raise SystemExit('Nom de membre normalisé ambigu')
            normalized[name]=m
        names=list(normalized)
        activity=[n for n in names if n.startswith('activities/') and n.endswith('/module.xml')]
        types=dict(sorted(collections.Counter(n.split('/')[1].split('_')[0] for n in activity).items()))
        result={'backup_bytes':os.stat(a.backup).st_size,'archive_entries':len(names),'module_count':len(activity),'module_types':types}
        c=tf.extractfile(normalized['course/course.xml']) if 'course/course.xml' in names else None
        if c:
            raw=c.read(2*1024*1024+1)
            if len(raw)>2*1024*1024:raise SystemExit('Métadonnées du cours trop volumineuses')
            root=ET.fromstring(raw)
            result['course_format']=root.findtext('format')
        out=json.dumps(result,indent=2,ensure_ascii=False)
        if a.output:open(a.output,'x',encoding='utf-8').write(out+'\n')
        else:print(out)
if __name__=='__main__':main()
