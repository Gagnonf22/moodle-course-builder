"""Retouches sur sauvegardes synthétiques : graphe, refus et préservation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mbz_archive import reemballer, extraire
from mbz_cours import Cours, ecrire_xml
from integrer_h5p_sections import integrer
from ajouter_certificat import ajouter


def fields(root, **values):
    for name, value in values.items():
        ET.SubElement(root, name).text = str(value)
    return root


def fixture(root, *, template=False):
    root.mkdir()
    backup = ET.Element('moodle_backup')
    info = ET.SubElement(backup, 'information')
    ET.SubElement(info, 'original_course_contextid').text = '401'
    contents = ET.SubElement(info, 'contents')
    activities = ET.SubElement(contents, 'activities')
    ET.SubElement(info, 'settings')
    files = ET.Element('files')
    layout = [(101, 0, [73, 21]), (102, 1, [17])] if not template else [(601, 0, [607])]
    for sid, num, mids in layout:
        section = fields(ET.Element('section', id=str(sid)), number=num, name=f'Section {num}',
                         summary='<p>Orientation</p><aside>Condition</aside>', summaryformat=1,
                         sequence=','.join(map(str, mids)), visible=1, availabilityjson='$@NULL@$')
        path = root / f'sections/section_{sid}/section.xml'
        path.parent.mkdir(parents=True)
        ecrire_xml(path, section)
        for mid in mids:
            kind = 'customcert' if template else 'h5pactivity'
            ctx, instance = mid + 1000, mid + 2000
            folder = root / f'activities/{kind}_{mid}'
            folder.mkdir(parents=True)
            module = fields(ET.Element('module', id=str(mid), version='2025000001'), modulename=kind,
                            sectionid=sid, sectionnumber=num, idnumber=f'activity-{mid}', added=42,
                            visible=1, visibleoncoursepage=1, visibleold=1, groupmode=0, groupingid=0,
                            completion=2, completionview=0, completionpassgrade=1 if mid == 17 else 0,
                            completiongradeitemnumber=0, availability='$@NULL@$', showdescription=0)
            ecrire_xml(folder / 'module.xml', module)
            detail = ET.Element('activity', id=str(instance), moduleid=str(mid), modulename=kind, contextid=str(ctx))
            obj = fields(ET.SubElement(detail, kind, id=str(instance)), name=f'Activity {mid}')
            if not template:
                raw = f'fake-h5p-{mid}'.encode()
                sha = hashlib.sha1(raw).hexdigest()
                blob = root / f'files/{sha[:2]}/{sha}'
                blob.parent.mkdir(parents=True, exist_ok=True)
                blob.write_bytes(raw)
                fields(ET.SubElement(files, 'file', id=str(mid + 3000)), component='mod_h5pactivity',
                       filearea='package', contextid=ctx, itemid=0, filepath='/', filename=f'video-{mid}.h5p',
                       contenthash=sha, filesize=len(raw))
            else:
                fields(obj, templateid=619, intro='<p>Old</p>', emailstudents=1, emailteachers=1,
                       emailothers='recipient-synthetic', issueautomatically=1, timecreated=42, timemodified=42)
                issues = ET.SubElement(obj, 'issues')
                fields(ET.SubElement(issues, 'issue'), userid=888, code='DO-NOT-COPY-ISSUE')
                model = fields(ET.SubElement(obj, 'template', id='619'), name='Model', contextid=ctx,
                               timecreated=42, timemodified=42)
                page = fields(ET.SubElement(ET.SubElement(model, 'pages'), 'page', id='631'),
                              templateid=619, width=279, height=216, leftmargin=0, rightmargin=0,
                              sequence=1, timecreated=42, timemodified=42)
                image = dict(width=0, height=0, contextid=str(ctx), filearea='image', itemid='0', filepath='/', filename='old.png')
                for eid, typ, data in [(641, 'bgimage', json.dumps(image)), (643, 'studentname', ''),
                                       (647, 'date', json.dumps(dict(dateitem='-1', dateformat='strftimedate')))]:
                    fields(ET.SubElement(page, 'element', id=str(eid)), pageid=631, element=typ, data=data,
                           timecreated=42, timemodified=42)
            ecrire_xml(folder / f'{kind}.xml', detail)
            fields(ET.SubElement(activities, 'activity'), moduleid=mid, sectionid=sid, modulename=kind,
                   title=f'Activity {mid}', directory=f'activities/{kind}_{mid}', insubsection='')
    ecrire_xml(root / 'moodle_backup.xml', backup)
    ecrire_xml(root / 'files.xml', files)


class RetouchesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mbzr-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.course = self.root / 'course'
        self.model = self.root / 'model'
        fixture(self.course)
        fixture(self.model, template=True)
        self.src, self.ref = self.root / 'source.mbz', self.root / 'reference.mbz'
        self.image = self.root / 'background.png'
        self.image.write_bytes(b'\x89PNG\r\n\x1a\nsynthetic-not-decoded')
        self.config = dict(identifiant='recognition', nom='Certificate & Example', intro_html='<p>Well done & thanks</p>',
                           fond=str(self.image), section={'numero': 1}, condition={'idnumber': 'activity-17'}, horodatage=123)
        self.pack()

    def pack(self):
        # Sources de test refabriquées uniquement dans leur temporaire privé.
        self.src.unlink(missing_ok=True)
        self.ref.unlink(missing_ok=True)
        reemballer(self.course, self.src)
        reemballer(self.model, self.ref)

    def edit(self, base, relative, fn):
        path = base / relative
        tree = ET.parse(path).getroot()
        fn(tree)
        ecrire_xml(path, tree)
        self.pack()

    def unpack(self, source):
        out = self.root / ('unpacked-' + str(len(list(self.root.glob('unpacked-*')))))
        extraire(source, out)
        return Cours(out)

    def cert(self, dst, config=None):
        return ajouter(self.src, self.ref, config or self.config, dst, modele_selector={'type': 'customcert'})

    def test_h5p_sequence_contexts_visibility_and_preservation(self):
        original = hashlib.sha256(self.src.read_bytes()).hexdigest()
        dst = self.root / 'embedded.mbz'
        report = integrer(self.src, dst, ancre='<aside>')
        out = self.unpack(dst)
        summary = out.sections[101]['tree'].findtext('summary')
        self.assertLess(summary.index('video-73.h5p'), summary.index('video-21.h5p'))
        self.assertLess(summary.index('h5p-placeholder'), summary.index('<aside>'))
        for mid in (73, 21, 17):
            self.assertEqual(out.modules[mid]['tree'].findtext('visible'), '1')
            self.assertEqual(out.modules[mid]['tree'].findtext('visibleoncoursepage'), '0')
        self.assertIn('$@PLUGINFILEBYCONTEXT*1073@$', summary)
        self.assertEqual(len(report), 3)
        self.assertEqual(hashlib.sha256(self.src.read_bytes()).hexdigest(), original)
        self.assertEqual((out.root / 'files.xml').read_bytes(), (self.course / 'files.xml').read_bytes())

    def test_h5p_subset_and_double_application_refused(self):
        dst = self.root / 'subset.mbz'
        integrer(self.src, dst, modules=[17])
        out = self.unpack(dst)
        self.assertNotIn('h5p-placeholder', out.sections[101]['tree'].findtext('summary'))
        self.assertEqual(out.modules[73]['tree'].findtext('visibleoncoursepage'), '1')
        with self.assertRaises(ValueError):
            integrer(dst, self.root / 'double.mbz', modules=[17])
        self.assertFalse((self.root / 'double.mbz').exists())

    def test_h5p_missing_ambiguous_anchor_and_unknown_module_refused(self):
        for kwargs in ({'ancre':'missing'}, {'modules':[9999]}, {'modules':[17,17]}, {'modules':[]}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                integrer(self.src, self.root / 'no.mbz', **kwargs)
            self.assertFalse((self.root / 'no.mbz').exists())
        self.edit(self.course, 'sections/section_101/section.xml',
                  lambda t: setattr(t.find('summary'), 'text', '<aside></aside><aside></aside>'))
        with self.assertRaises(ValueError):
            integrer(self.src, self.root / 'no.mbz', ancre='<aside>')

    def test_h5p_missing_blob_and_ambiguous_package_refused(self):
        pool = next((self.course / 'files').rglob('*' + hashlib.sha1(b'fake-h5p-73').hexdigest()))
        pool.unlink()
        self.pack()
        with self.assertRaises(ValueError):
            integrer(self.src, self.root / 'no.mbz')
        fixture_dir = self.root / 'another'
        fixture(fixture_dir)
        self.course = fixture_dir
        def duplicate(t):
            row = copy.deepcopy(t.find('file'))
            row.set('id','9998')
            t.append(row)
        self.edit(self.course, 'files.xml', duplicate)
        with self.assertRaises(ValueError):
            integrer(self.src, self.root / 'no.mbz')

    def test_h5p_restrictions_hidden_and_existing_marker_refused(self):
        for field, value in [('visible','0'), ('availability',json.dumps(dict(type='completion',cm=17,e=1)))]:
            tree = ET.parse(self.course / 'activities/h5pactivity_73/module.xml').getroot()
            original = tree.findtext(field)
            self.edit(self.course, 'activities/h5pactivity_73/module.xml', lambda t: setattr(t.find(field),'text',value))
            with self.assertRaises(ValueError):
                integrer(self.src,self.root/'no.mbz')
            self.edit(self.course, 'activities/h5pactivity_73/module.xml',lambda t:setattr(t.find(field),'text',original))
        self.edit(self.course, 'sections/section_101/section.xml',lambda t:setattr(t.find('summary'),'text','<div class="h5p-placeholder"></div>'))
        with self.assertRaises(ValueError):
            integrer(self.src,self.root/'no.mbz')

    def test_certificate_allocates_ids_and_updates_all_added_references(self):
        before = Cours(self.course)
        digest = hashlib.sha256(self.src.read_bytes()).hexdigest()
        dst = self.root / 'certificate.mbz'
        ids = self.cert(dst)
        out = self.unpack(dst)
        self.assertTrue(set(ids[k] for k in ['module','contexte','instance','modele','page','fichier']).isdisjoint(before.ids))
        mod = out.modules[ids['module']]
        self.assertEqual(out.sections[102]['sequence'], [17, ids['module']])
        self.assertEqual(mod['tree'].findtext('idnumber'), 'recognition')

        # Contrat du détecteur convert_helper::detect_moodle2_format de Moodle :
        # un XML équivalent à guillemets simples ne suffit pas à identifier le .mbz.
        prefix = (out.root/'moodle_backup.xml').read_bytes()[:200]
        self.assertIn(b'<?xml version="1.0" encoding="utf-8"?>', prefix.lower())
        self.assertIn(b'<moodle_backup>', prefix)
        self.assertIn(b'<information>', prefix)
        self.assertEqual(json.loads(mod['tree'].findtext('availability'))['c'][0]['cm'],17)
        detail = mod['detail']
        obj = detail.find('customcert')
        self.assertEqual(detail.get('contextid'),str(ids['contexte']))
        self.assertEqual(obj.get('id'),str(ids['instance']))
        self.assertEqual(obj.findtext('templateid'),str(ids['modele']))
        page = obj.find('./template/pages/page')
        self.assertEqual(page.get('id'),str(ids['page']))
        self.assertEqual(page.findtext('templateid'),str(ids['modele']))
        for el in page.findall('element'):
            self.assertEqual(el.findtext('pageid'),str(ids['page']))
        bg = json.loads(page.find('element/data').text)
        self.assertEqual(bg['contextid'], '401')
        self.assertEqual(bg['filename'],'background.png')
        row = out.file_rows[ids['fichier']]
        self.assertEqual(out.blob(row).read_bytes(),self.image.read_bytes())
        self.assertEqual(row.findtext('author'),'')
        self.assertEqual(obj.findtext('name'),self.config['nom'])
        self.assertEqual(obj.findtext('intro'),self.config['intro_html'])
        self.assertEqual(len(obj.find('issues')),0)
        self.assertNotIn('DO-NOT-COPY-ISSUE',(out.root/mod['directory']/'customcert.xml').read_text())
        self.assertEqual(obj.findtext('emailstudents'),'0')
        declaration = out.backup.findall('./information/contents/activities/activity')[-1]
        self.assertEqual(declaration.findtext('moduleid'),str(ids['module']))
        inforef = ET.parse(out.root/mod['directory']/'inforef.xml').getroot()
        self.assertEqual(inforef.findtext('./fileref/file/id'),str(ids['fichier']))
        self.assertEqual(hashlib.sha256(self.src.read_bytes()).hexdigest(),digest)

    def test_certificate_double_application_and_existing_output_refused(self):
        dst = self.root/'certificate.mbz'
        self.cert(dst)
        digest = hashlib.sha256(dst.read_bytes()).hexdigest()
        with self.assertRaises(FileExistsError):self.cert(dst)
        with self.assertRaises(ValueError):
            ajouter(dst,self.ref,self.config,self.root/'double.mbz',modele_selector={'type':'customcert'})
        self.assertFalse((self.root/'double.mbz').exists())
        self.assertEqual(hashlib.sha256(dst.read_bytes()).hexdigest(),digest)

    def test_certificate_selectors_and_pass_condition_refused(self):
        for change in [dict(section={'nom':'unknown'}),dict(condition={'type':'h5pactivity'}),
                       dict(condition={'id':21}),dict(identifiant='../bad')]:
            with self.assertRaises(ValueError):self.cert(self.root/'no.mbz',dict(self.config,**change))
            self.assertFalse((self.root/'no.mbz').exists())

    def test_certificate_unsupported_template_and_bad_image_refused(self):
        self.edit(self.model, 'activities/customcert_607/customcert.xml',
                  lambda t:setattr(t.find('./customcert/template/pages/page/element/element'),'text','unknown'))
        with self.assertRaises(ValueError):self.cert(self.root/'no.mbz')
        self.image.write_bytes(b'not-png')
        with self.assertRaises(ValueError):self.cert(self.root/'no.mbz')
        self.assertFalse((self.root/'no.mbz').exists())

    def test_certificate_partial_model_restriction_is_replaced_not_copied(self):
        self.edit(self.model,'activities/customcert_607/module.xml',
                  lambda t:setattr(t.find('availability'),'text',json.dumps(dict(type='completion',cm=99999,e=1))))
        dst=self.root/'certificate.mbz'
        ids=self.cert(dst)
        out=self.unpack(dst)
        self.assertNotIn('99999',out.modules[ids['module']]['tree'].findtext('availability'))

    def test_inconsistent_sequence_and_dangling_restriction_refused(self):
        self.edit(self.course,'sections/section_101/section.xml',lambda t:setattr(t.find('sequence'),'text','73,99999'))
        with self.assertRaises(ValueError):integrer(self.src,self.root/'no.mbz')
        self.edit(self.course,'sections/section_101/section.xml',lambda t:setattr(t.find('sequence'),'text','73,21'))
        self.edit(self.course,'activities/h5pactivity_73/module.xml',
                  lambda t:setattr(t.find('availability'),'text',json.dumps(dict(type='completion',cm=99999,e=1))))
        with self.assertRaises(ValueError):self.cert(self.root/'no.mbz')

    def test_h5p_other_context_links_preserved_and_hidden_section_refused(self):
        html='<img src="$@PLUGINFILEBYCONTEXT*900@$/course/section/image.png"><aside>Condition</aside>'
        self.edit(self.course,'sections/section_101/section.xml',lambda t:setattr(t.find('summary'),'text',html))
        dst=self.root/'with-image.mbz'
        integrer(self.src,dst)
        self.assertIn(html,self.unpack(dst).sections[101]['tree'].findtext('summary'))
        self.edit(self.course,'sections/section_101/section.xml',lambda t:setattr(t.find('visible'),'text','0'))
        with self.assertRaises(ValueError):integrer(self.src,self.root/'no.mbz')

    def test_duplicate_file_ids_and_corrupted_payload_refused(self):
        def duplicate(t):t.append(copy.deepcopy(t.find('file')))
        self.edit(self.course,'files.xml',duplicate)
        with self.assertRaises(ValueError):integrer(self.src,self.root/'no.mbz')
        fresh=self.root/'fresh'
        fixture(fresh)
        self.course=fresh
        row=ET.parse(fresh/'files.xml').getroot().find('file')
        sha=row.findtext('contenthash')
        (fresh/f'files/{sha[:2]}/{sha}').write_bytes(b'corrupted')
        self.pack()
        with self.assertRaises(ValueError):integrer(self.src,self.root/'no.mbz')

    def test_certificate_multiple_pages_and_unknown_fields_refused(self):
        def second_page(t):
            pages=t.find('./customcert/template/pages')
            pages.append(copy.deepcopy(pages.find('page')))
        self.edit(self.model,'activities/customcert_607/customcert.xml',second_page)
        with self.assertRaises(ValueError):self.cert(self.root/'no.mbz')
        fresh=self.root/'newmodel'
        fixture(fresh,template=True)
        self.model=fresh
        self.edit(self.model,'activities/customcert_607/customcert.xml',
                  lambda t:ET.SubElement(t.find('customcert'),'participants'))
        with self.assertRaises(ValueError):self.cert(self.root/'no.mbz')
        self.assertFalse((self.root/'no.mbz').exists())

    def test_certificate_plugin_version_mismatch_refused(self):
        first=self.root/'first.mbz'
        self.cert(first)
        self.edit(self.model,'activities/customcert_607/module.xml',lambda t:t.set('version','2025999999'))
        config=dict(self.config,identifiant='another',nom='Another certificate')
        with self.assertRaisesRegex(ValueError,'Versions customcert'):
            ajouter(first,self.ref,config,self.root/'no.mbz',modele_selector={'type':'customcert'})
        self.assertFalse((self.root/'no.mbz').exists())

    def add_model_image(self):
        raw = b'\x89PNG\r\n\x1a\nsynthetic-signature'
        sha = hashlib.sha1(raw).hexdigest()
        blob = self.model / f'files/{sha[:2]}/{sha}'
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_bytes(raw)
        path = self.model/'activities/customcert_607/customcert.xml'
        tree = ET.parse(path).getroot()
        fields(ET.SubElement(tree.find('./customcert/template/pages/page'), 'element', id='650'),
               pageid=631, element='image', data=json.dumps(dict(contextid='1607', filearea='image',
               itemid='0', filepath='/', filename='signature.png', width=50, alphachannel=1)))
        ecrire_xml(path, tree)
        files = ET.parse(self.model/'files.xml').getroot()
        fields(ET.SubElement(files, 'file', id='555'), component='mod_customcert', filearea='image',
               contextid=1607, itemid=0, filepath='/', filename='signature.png', contenthash=sha, filesize=len(raw))
        ecrire_xml(self.model/'files.xml', files)
        self.pack()
        return raw

    def test_certificate_image_blob_context_and_inforef(self):
        raw = self.add_model_image()
        dst = self.root/'signature.mbz'
        ids = self.cert(dst)
        out = self.unpack(dst)
        self.assertEqual(len(ids['fichiers']), 2)
        row = out.file_rows[ids['fichiers'][1]]
        self.assertEqual(out.blob(row).read_bytes(), raw)
        self.assertEqual(row.findtext('userid'), '$@NULL@$')
        self.assertEqual(row.findtext('contextid'), '401')
        self.assertNotEqual(ids['contexte_images'],ids['contexte'])
        el = next(el for el in out.modules[ids['module']]['detail'].findall('.//page/element')
                  if el.findtext('element') == 'image')
        self.assertEqual(json.loads(el.findtext('data'))['contextid'], '401')
        refs = ET.parse(out.root/out.modules[ids['module']]['directory']/'inforef.xml').getroot()
        self.assertEqual({int(x.text) for x in refs.findall('./fileref/file/id')}, set(ids['fichiers']))

    def test_certificate_image_missing_ambiguous_corrupt_or_wrong_context_refused(self):
        self.add_model_image()
        original = (self.model/'files.xml').read_bytes()
        for mutation in ('missing', 'duplicate', 'context', 'corrupt'):
            with self.subTest(mutation=mutation):
                tree = ET.fromstring(original)
                row = tree.find('file')
                if mutation == 'missing': tree.remove(row)
                if mutation == 'duplicate':
                    another = copy.deepcopy(row); another.set('id','556'); tree.append(another)
                if mutation == 'context': row.find('contextid').text='999'
                if mutation == 'corrupt':
                    sha = row.findtext('contenthash')
                    (self.model/f'files/{sha[:2]}/{sha}').write_bytes(b'corrupt')
                ecrire_xml(self.model/'files.xml', tree)
                self.pack()
                with self.assertRaises(ValueError): self.cert(self.root/'no.mbz')
                self.assertFalse((self.root/'no.mbz').exists())

    def test_certificate_image_background_name_collision_refused(self):
        self.add_model_image()
        alt = self.root/'signature.png'
        alt.write_bytes(self.image.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Collision'):
            self.cert(self.root/'no.mbz',dict(self.config,fond=str(alt)))

    def test_certificate_image_can_reference_a_different_source_context(self):
        self.add_model_image()
        def change_context(tree):
            for el in tree.findall('.//page/element'):
                if el.findtext('element') in {'image','bgimage'}:
                    data=json.loads(el.findtext('data')); data['contextid']='9017'
                    el.find('data').text=json.dumps(data)
        self.edit(self.model,'activities/customcert_607/customcert.xml',change_context)
        self.edit(self.model,'files.xml',lambda t:setattr(t.find('file/contextid'),'text','9017'))
        ids=self.cert(self.root/'shared.mbz')
        self.assertEqual(len(ids['fichiers']),2)

    def test_certificate_missing_course_context_refused(self):
        self.edit(self.course,'moodle_backup.xml',lambda t:t.find('information').remove(t.find('./information/original_course_contextid')))
        with self.assertRaises(ValueError): self.cert(self.root/'no.mbz')
        self.assertFalse((self.root/'no.mbz').exists())

    def test_certificate_existing_course_image_name_refused(self):
        def conflict(t):
            fields(ET.SubElement(t,'file',id='9991'),contextid=401,component='mod_customcert',
                   filearea='image',itemid=0,filepath='/',filename=self.image.name)
        self.edit(self.course,'files.xml',conflict)
        with self.assertRaisesRegex(ValueError,'déjà présent'): self.cert(self.root/'no.mbz')
        self.assertFalse((self.root/'no.mbz').exists())


if __name__ == '__main__':
    unittest.main()
