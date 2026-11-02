"""Ajouter un Custom certificate depuis un modèle explicite, sur copie TAR/gzip."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import time
import xml.etree.ElementTree as ET

from mbz_archive import extraire, reemballer
from mbz_cours import Cours, entier, champ, nom_fichier, ecrire_xml

VIDES = {
    'roles.xml': ('roles', ('role_overrides', 'role_assignments')),
    'filters.xml': ('filters', ('filter_actives', 'filter_configs')),
    'grades.xml': ('activity_gradebook', ('grade_items', 'grade_letters')),
    'grade_history.xml': ('grade_history', ('grade_grades',)),
    'calendar.xml': ('events', ()),
    'competencies.xml': ('course_module_competencies', ('competencies',)),
}


def configuration(value):
    allowed = {'identifiant', 'nom', 'intro_html', 'section', 'condition', 'fond', 'auteur', 'licence', 'horodatage'}
    if not isinstance(value, dict) or value.keys() - allowed:
        raise ValueError('Configuration de certificat invalide ou champs inconnus')
    for key in ('identifiant', 'nom', 'intro_html', 'fond'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError(f'Champ de certificat requis : {key}')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value['identifiant']):
        raise ValueError('Identifiant logique de certificat invalide')
    for key in ('auteur', 'licence'):
        if key in value and not isinstance(value[key], str):
            raise ValueError('Auteur et licence doivent être textuels')
    if 'horodatage' in value and (type(value['horodatage']) is not int or value['horodatage'] < 0):
        raise ValueError('Horodatage entier positif ou nul attendu')
    return value


def modele(reference, selector):
    mod = reference.choisir(selector)
    if mod['type'] != 'customcert' or mod['detail'] is None:
        raise ValueError('Une activité modèle customcert est requise')
    activity = copy.deepcopy(mod['detail'])
    if (activity.tag != 'activity' or activity.get('modulename') != 'customcert' or
            activity.get('moduleid') != str(mod['id'])):
        raise ValueError('Racine de modèle de certificat incohérente')
    obj = activity.find('customcert')
    if obj is None or activity.get('id') != obj.get('id'):
        raise ValueError('Instance du modèle incohérente')
    fields = {'templateid', 'name', 'intro', 'introformat', 'requiredtime', 'verifyany', 'deliveryoption',
              'usecustomfilename', 'customfilenamepattern', 'emailstudents', 'emailteachers', 'emailothers',
              'issueautomatically', 'completionemailed', 'protection', 'language', 'timecreated', 'timemodified',
              'issues', 'template'}
    if ([z.tag for z in activity] != ['customcert'] or any(z.tag not in fields for z in obj)
            or len({z.tag for z in obj}) != len(obj)
            or any(len(z) for z in obj if z.tag not in {'issues', 'template'})):
        raise ValueError('Champs de modèle customcert non gérés')
    template = obj.find('template')
    pages = template.findall('./pages/page') if template is not None else []
    if template is None or len(pages) != 1 or obj.findtext('templateid') != template.get('id'):
        raise ValueError('Ce profil exige un modèle de certificat à une page')
    if (any(z.tag not in {'name','contextid','timecreated','timemodified','pages'} for z in template)
            or len({z.tag for z in template}) != len(template)):
        raise ValueError('Champs de template non gérés')
    page = pages[0]
    if page.findtext('templateid') != template.get('id'):
        raise ValueError('Référence de page incohérente')
    # Le profil du prototype place les éléments directement sous page.
    elements = page.findall('element')
    if not elements or page.find('elements') is not None:
        raise ValueError('Structure des éléments du modèle non gérée')
    if any(z.tag not in {'templateid','width','height','leftmargin','rightmargin','sequence',
                        'timecreated','timemodified','element'} for z in page):
        raise ValueError('Champs de page non gérés')
    backgrounds = []
    for el in elements:
        if (any(z.tag not in {'pageid','name','element','data','font','fontsize','colour','posx','posy',
                              'width','refpoint','sequence','alignment','timecreated','timemodified'} for z in el)
                or len({z.tag for z in el}) != len(el) or any(len(z) for z in el)):
            raise ValueError('Champs d’élément non gérés')
        if el.findtext('pageid') != page.get('id'):
            raise ValueError('Référence d’élément incohérente')
        kind = el.findtext('element')
        if kind not in {'bgimage', 'image', 'studentname', 'date', 'code', 'text', 'coursename'}:
            raise ValueError('Type d’élément de certificat non géré par ce profil')
        if kind == 'date':
            data = json.loads(el.findtext('data') or '{}')
            if data.get('dateitem') != '-1':
                raise ValueError('Seule la date de délivrance sans référence d’activité est admise')
        if kind == 'bgimage':
            backgrounds.append(el)
    if len(backgrounds) != 1:
        raise ValueError('Une seule image de fond est requise dans le modèle')
    bgdata = json.loads(backgrounds[0].findtext('data') or '{}')
    if (not isinstance(bgdata, dict) or not re.fullmatch(r'[1-9][0-9]*', str(bgdata.get('contextid')))
            or bgdata.get('filearea') != 'image'
            or str(bgdata.get('itemid')) != '0' or bgdata.get('filepath') != '/'):
        raise ValueError('Références de fond du modèle non gérées')
    # On ne transporte ni émissions, ni destinataires d'email du modèle.
    issues = obj.find('issues')
    if issues is None:
        raise ValueError('Conteneur issues requis')
    issues.clear()
    for key in ('emailstudents', 'emailteachers', 'issueautomatically'):
        champ(obj, key, 0)
    champ(obj, 'emailothers', '')
    version = mod['tree'].get('version')
    if not isinstance(version, str) or not re.fullmatch('[0-9]+', version):
        raise ValueError('Version du plugin modèle requise')
    return mod, activity, obj, template, page, backgrounds[0], bgdata


def images_modele(reference, activity, page, background_name):
    """Ne reprendre que les PNG effectivement référencés, sans métadonnées utilisateur."""
    images = {}
    for el in page.findall('element'):
        if el.findtext('element') != 'image':
            continue
        data = json.loads(el.findtext('data') or '{}')
        if (not isinstance(data, dict) or not re.fullmatch(r'[1-9][0-9]*', str(data.get('contextid')))
                or data.get('filearea') != 'image' or str(data.get('itemid')) != '0'
                or data.get('filepath') != '/'):
            raise ValueError('Références d’image du modèle non gérées')
        name = nom_fichier(data.get('filename', ''))
        if name == background_name:
            raise ValueError('Collision entre nom du fond et image du modèle')
        rows = [r for r in reference.file_rows.values()
                if r.findtext('contextid') == str(data['contextid'])
                and r.findtext('component') == 'mod_customcert' and r.findtext('filearea') == 'image'
                and r.findtext('itemid') == '0' and r.findtext('filepath') == '/'
                and r.findtext('filename') == name]
        if len(rows) != 1:
            raise ValueError('Image du modèle absente ou ambiguë')
        path = reference.blob(rows[0])
        if path.stat().st_size > 32 * 1024**2:
            raise ValueError('Image du modèle trop grande (32 Mio maximum)')
        raw = path.read_bytes()
        if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Image du modèle : PNG de 32 Mio maximum requis')
        images[name] = raw
    return images


def ajouter(src, reference_mbz, config, dst, *, modele_selector, base_config=None):
    config = configuration(config)
    if Path(dst).exists():
        raise FileExistsError('Sortie existante refusée')
    background = Path(config['fond'])
    if not background.is_absolute():
        background = Path(base_config or '.') / background
    if not background.is_file() or background.stat().st_size > 32 * 1024**2:
        raise ValueError('Image de fond absente ou trop grande (32 Mio maximum)')
    data = background.read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Ce profil exige un fond PNG')
    filename = nom_fichier(background.name)
    now = config.get('horodatage', int(time.time()))
    with tempfile.TemporaryDirectory(prefix='mbzc-') as tmp:
        target_dir, model_dir = Path(tmp) / 'c', Path(tmp) / 'r'
        extraire(src, target_dir)
        extraire(reference_mbz, model_dir)
        # Une référence partielle peut contenir d'anciennes restrictions :
        # seules la définition contrôlée et la page sont reprises, pas ces restrictions.
        cours, ref = Cours(target_dir), Cours(model_dir, verifier_dependances=False)
        # Custom certificate restaure les images dans le contexte du COURS,
        # puis after_restore réécrit les éléments vers ce contexte (pas le module).
        image_context = entier(cours.backup.findtext('./information/original_course_contextid'))
        sec = cours.choisir(config.get('section'), section=True)
        condition = cours.choisir(config.get('condition'))
        if (condition['tree'].findtext('completion') != '2' or
                condition['tree'].findtext('completionpassgrade') != '1' or
                condition['tree'].findtext('visible') != '1'):
            raise ValueError('L’activité condition doit déjà exiger un achèvement automatique avec réussite')
        if any(m['idnumber'] == config['identifiant'] or
               m['type'] == 'customcert' and m['nom'] == config['nom'] for m in cours.modules.values()):
            raise ValueError('Certificat déjà présent : double application ou nom ambigu refusé')
        mod, activity, obj, template, page, bg, bgdata = modele(ref, modele_selector)
        images = images_modele(ref, activity, page, filename)
        if any(m['type'] == 'customcert' and m['tree'].get('version') != mod['tree'].get('version')
               for m in cours.modules.values()):
            raise ValueError('Versions customcert incohérentes entre modèle et destination')
        image_names = {filename, *images}
        if any(row.findtext('contextid') == str(image_context) and row.findtext('component') == 'mod_customcert'
               and row.findtext('filearea') == 'image' and row.findtext('itemid') == '0'
               and row.findtext('filepath') == '/' and row.findtext('filename') in image_names
               for row in cours.file_rows.values()):
            raise ValueError('Nom d’image déjà présent dans le contexte du cours')
        module, context, instance, template_id, page_id, file_id = [cours.nouveau_id() for _ in range(6)]
        directory = f'activities/customcert_{module}'
        folder = target_dir / directory
        folder.mkdir()
        activity.attrib.update(id=str(instance), moduleid=str(module), contextid=str(context))
        obj.set('id', str(instance))
        champ(obj, 'templateid', template_id)
        champ(obj, 'name', config['nom'])
        champ(obj, 'intro', config['intro_html'])
        template.set('id', str(template_id))
        champ(template, 'name', config['nom'])
        champ(template, 'contextid', context)
        page.set('id', str(page_id))
        champ(page, 'templateid', template_id)
        for el in page.findall('element'):
            el.set('id', str(cours.nouveau_id()))
            champ(el, 'pageid', page_id)
            if el.findtext('element') == 'image':
                image_data = json.loads(el.findtext('data'))
                image_data['contextid'] = str(image_context)
                champ(el, 'data', json.dumps(image_data, ensure_ascii=False, separators=(',', ':')))
        bgdata.update(contextid=str(image_context), filearea='image', itemid='0', filepath='/', filename=filename)
        champ(bg, 'data', json.dumps(bgdata, ensure_ascii=False, separators=(',', ':')))
        for el in activity.iter():
            if el.tag in {'timecreated', 'timemodified'}:
                el.text = str(now)
        ecrire_xml(folder / 'customcert.xml', activity)

        module_xml = copy.deepcopy(mod['tree'])
        module_xml.set('id', str(module))
        for key, value in dict(sectionid=sec['id'], sectionnumber=sec['numero'], idnumber=config['identifiant'],
                               added=now, visible=1, visibleoncoursepage=1, visibleold=1, groupmode=0, groupingid=0,
                               completion=2, completionview=1, completionpassgrade=0,
                               completiongradeitemnumber='$@NULL@$', showdescription=1).items():
            champ(module_xml, key, value)
        availability = dict(op='&', c=[dict(type='completion', cm=condition['id'], e=1)], showc=[True])
        champ(module_xml, 'availability', json.dumps(availability, separators=(',', ':')))
        tags = module_xml.find('tags')
        if tags is not None:
            tags.clear()
        ecrire_xml(folder / 'module.xml', module_xml)
        for filename_xml, (tag, children) in VIDES.items():
            # Construction de conteneurs vides : aucune trace utilisateur importée.
            tree = ET.Element(tag)
            for child in children:
                ET.SubElement(tree, child)
            ecrire_xml(folder / filename_xml, tree)
        info = ET.Element('inforef')
        ET.SubElement(ET.SubElement(ET.SubElement(info, 'fileref'), 'file'), 'id').text = str(file_id)
        ecrire_xml(folder / 'inforef.xml', info)

        sha = hashlib.sha1(data).hexdigest()
        blob = target_dir / 'files' / sha[:2] / sha
        blob.parent.mkdir(parents=True, exist_ok=True)
        if blob.exists() and blob.read_bytes() != data:
            raise ValueError('Collision de contenu du fichier de fond')
        blob.write_bytes(data)
        file_row = ET.SubElement(cours.files, 'file', id=str(file_id))
        fields = dict(contenthash=sha, contextid=image_context, component='mod_customcert', filearea='image', itemid=0,
                      filepath='/', filename=filename, userid='$@NULL@$', filesize=len(data), mimetype='image/png',
                      status=0, timecreated=now, timemodified=now, source=filename,
                      author=config.get('auteur', ''), license=config.get('licence', 'allrightsreserved'), sortorder=0,
                      repositorytype='$@NULL@$', repositoryid='$@NULL@$', reference='$@NULL@$')
        for key, value in fields.items():
            ET.SubElement(file_row, key).text = str(value)
        file_ids = [file_id]
        for image_name, image_raw in images.items():
            image_id = cours.nouveau_id()
            image_sha = hashlib.sha1(image_raw).hexdigest()
            image_blob = target_dir / 'files' / image_sha[:2] / image_sha
            image_blob.parent.mkdir(parents=True, exist_ok=True)
            if image_blob.exists() and image_blob.read_bytes() != image_raw:
                raise ValueError('Collision de contenu d’image')
            image_blob.write_bytes(image_raw)
            image_row = ET.SubElement(cours.files, 'file', id=str(image_id))
            for key, value in dict(fields, contenthash=image_sha, filename=image_name,
                                   source=image_name, filesize=len(image_raw)).items():
                ET.SubElement(image_row, key).text = str(value)
            ET.SubElement(ET.SubElement(info.find('fileref'), 'file'), 'id').text = str(image_id)
            file_ids.append(image_id)
        ecrire_xml(folder / 'inforef.xml', info)
        champ(sec['tree'], 'sequence', ','.join(map(str, sec['sequence'] + [module])))
        contents = cours.backup.find('./information/contents/activities')
        settings = cours.backup.find('./information/settings')
        if contents is None or settings is None:
            raise ValueError('Déclarations des activités et réglages de sauvegarde requis')
        declaration = ET.SubElement(contents, 'activity')
        for key, value in dict(moduleid=module, sectionid=sec['id'], modulename='customcert', title=config['nom'],
                               directory=directory, insubsection='').items():
            ET.SubElement(declaration, key).text = str(value)
        for key, value in [('included', 1), ('userinfo', 0)]:
            setting = ET.SubElement(settings, 'setting')
            for field, val in dict(level='activity', activity=f'customcert_{module}',
                                  name=f'customcert_{module}_{key}', value=value).items():
                ET.SubElement(setting, field).text = str(val)
        cours.enregistrer(['files.xml', 'moodle_backup.xml', sec['path']])
        # Relire la structure écrite et vérifier les références propres à l'ajout.
        final = Cours(target_dir)
        added = final.modules[module]
        if added['section'] != sec['id'] or final.file_rows[file_id].findtext('contextid') != str(image_context):
            raise ValueError('Références ajoutées incohérentes')
        for fid in file_ids:
            final.blob(final.file_rows[fid])
        reemballer(target_dir, dst)
        return dict(module=module, contexte=context, contexte_images=image_context, instance=instance, modele=template_id,
                    page=page_id, fichier=file_id, fichiers=file_ids, section=sec['id'], condition=condition['id'], version=mod['tree'].get('version'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('sortie')
    p.add_argument('--reference', required=True, help='Sauvegarde contenant le modèle customcert')
    p.add_argument('--modele', required=True, help='Sélecteur JSON de l’activité customcert modèle')
    p.add_argument('--config', required=True, help='Configuration JSON du projet')
    a = p.parse_args()
    path = Path(a.config)
    result = ajouter(a.source, a.reference, json.loads(path.read_text(encoding='utf-8-sig')), a.sortie,
                     modele_selector=json.loads(a.modele), base_config=path.parent)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
