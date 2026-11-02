#!/usr/bin/env python3
"""Offline read-only structural Moodle backup inventory; no extraction."""
import argparse, collections, json, os, tarfile, xml.etree.ElementTree as ET

def main():
    p=argparse.ArgumentParser();p.add_argument('backup');p.add_argument('--output');a=p.parse_args()
    if not tarfile.is_tarfile(a.backup): raise SystemExit('Unsupported archive: not TAR')
    with tarfile.open(a.backup,'r:*') as tf:
        members=tf.getmembers()
        if len(members)>100000: raise SystemExit('Too many archive members')
        if any(m.issym() or m.islnk() or m.name.startswith('/') or '..' in m.name.split('/') for m in members):raise SystemExit('Unsafe member name/type')
        if sum(m.size for m in members)>8*1024**3: raise SystemExit('Uncompressed size exceeds inspection limit')
        normalized={}
        for m in members:
            name=m.name
            while name.startswith('./'):name=name[2:]
            if name in ('','.') and m.isdir():continue
            if name in normalized:raise SystemExit('Ambiguous normalized member name')
            normalized[name]=m
        names=list(normalized)
        activity=[n for n in names if n.startswith('activities/') and n.endswith('/module.xml')]
        types=dict(sorted(collections.Counter(n.split('/')[1].split('_')[0] for n in activity).items()))
        result={'backup_bytes':os.stat(a.backup).st_size,'archive_entries':len(names),'module_count':len(activity),'module_types':types}
        c=tf.extractfile(normalized['course/course.xml']) if 'course/course.xml' in names else None
        if c:
            raw=c.read(2*1024*1024+1)
            if len(raw)>2*1024*1024:raise SystemExit('Course metadata too large')
            root=ET.fromstring(raw)
            result['course_format']=root.findtext('format')
        out=json.dumps(result,indent=2,ensure_ascii=False)
        if a.output:open(a.output,'x',encoding='utf-8').write(out+'\n')
        else:print(out)
if __name__=='__main__':main()
