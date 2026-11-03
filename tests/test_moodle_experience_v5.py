"""Contrat v5 : actions, ressources et dépendances avant toute création Moodle."""
import copy
import json
import unittest
import test_moodle_livre_devoir as livre
import test_moodle_cli as cli


@unittest.skipUnless(cli.PHP, 'PHP_BIN requis')
class ExperienceV5Tests(unittest.TestCase):
    setUp = cli.MoodleCliTests.setUp
    helper = livre.LivreDevoirTests.helper

    def spec(self):
        (self.project/'section.html').write_text('<h2>Pratiquer</h2><p>Comparer puis remettre.</p>',encoding='utf8')
        (self.project/'depart.pdf').write_bytes(b'%PDF-1.4 synthetic')
        return dict(version=5,sections=[dict(summary='section.html',activities=[
            dict(type='glossary',idnumber='lexique',completion='none',entries=[
                dict(concept='Trace',definition='<p>Production remise.</p>')]),
            dict(type='assign',idnumber='pratique',completion='submit',grade=0,
                submission=dict(text=True,files=False),attachments=['depart.pdf'])])])

    def test_practice_without_grade_requires_no_grading(self):
        r=self.helper(self.spec(),'mcb_valider_structure($s,$p); $mi=new stdClass(); mcb_preparer_devoir($mi,$s->sections[0]->activities[1]); echo json_encode($mi);')
        self.assertEqual(r.returncode,0,r.stderr)
        d=json.loads(r.stdout)
        self.assertEqual(d['grade'],0)
        self.assertEqual(d['completionsubmit'],1)
        self.assertEqual(d['advancedgradingmethod_submissions'],'')
        for change in [dict(completion='pass'),dict(completion='grade'),dict(gradepass=1),dict(grading={})]:
            s=self.spec();s['sections'][0]['activities'][1].update(change)
            self.assertEqual(self.helper(s).returncode,2,change)

    def test_attachments_cannot_escape_project_or_collide(self):
        (self.root/'outside.pdf').write_bytes(b'outside')
        for paths in [['../outside.pdf'],['missing.pdf'],['depart.pdf','depart.pdf']]:
            s=self.spec();s['sections'][0]['activities'][1]['attachments']=paths
            self.assertEqual(self.helper(s).returncode,2,paths)

    def test_glossary_cannot_drop_definitions_or_duplicate_concepts(self):
        for entries in [[],[dict(concept='Trace',definition='')],
                        [dict(concept='Trace',definition='A'),dict(concept='Trace',definition='B')]]:
            s=self.spec();s['sections'][0]['activities'][0]['entries']=entries
            self.assertEqual(self.helper(s).returncode,2,entries)

    def test_v5_fields_refused_in_older_contract(self):
        for version in [1,2,3,4]:
            s=self.spec();s['version']=version
            self.assertEqual(self.helper(s).returncode,2)

    def test_unknown_or_repeated_h5p_token_refused(self):
        for html in ['{{h5p:missing}}','{{h5p:entrainement}}{{h5p:entrainement}}']:
            s=self.spec();s['sections'][0]['activities'].append(dict(type='h5p',idnumber='entrainement',completion='grade'))
            (self.project/'section.html').write_text(html,encoding='utf8')
            self.assertEqual(self.helper(s).returncode,2)

    def test_h5p_default_and_override_and_placement(self):
        s=self.spec();s['sections'][0]['activities'].append(dict(type='h5p',idnumber='entrainement',completion='grade',package='training.h5p'))
        (self.project/'section.html').write_text('<h2>Avant</h2>{{h5p:entrainement}}<p>Après</p>',encoding='utf8')
        code='''mcb_valider_structure($s,$p);
        define('MUST_EXIST',2);
        class context_module {static function instance($id){return (object)['id'=>$id+100];}}
        class DB {function get_field(...$x){return 7;}} $DB=new DB();
        $CFG=(object)['wwwroot'=>'http://localhost'];
        echo mcb_resume_section($s->sections[0],$p,42,5);'''
        r=self.helper(s,code);self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('/pluginfile.php/107/mod_h5pactivity/package/0/training.h5p',r.stdout)
        self.assertTrue(r.stdout.startswith('<h2>Avant</h2><div'))
        self.assertTrue(r.stdout.endswith('<p>Après</p>'))
        a=s['sections'][0]['activities'][-1];a['embed']=False
        self.assertEqual(self.helper(s).returncode,2)  # Existing token must not silently disappear.

    def quiz_spec(self):
        from test_moodle_tests_natifs import TestsNatifsTests
        s=TestsNatifsTests.spec(self);s['version']=5
        (self.project/'section.html').write_text('<p>Évaluer</p>',encoding='utf8')
        s['sections'][0]['summary']='section.html'
        a=s['sections'][0]['activities'][1];a.update(completion='submit',attempts=0)
        return s

    def test_quiz_unlimited_and_finished_attempt_are_independent_of_success(self):
        s=self.quiz_spec()
        r=self.helper(s,'mcb_valider_structure($s,$p);$mi=new stdClass();mcb_preparer_test($mi,$s->sections[0]->activities[1]);echo json_encode($mi);')
        self.assertEqual(r.returncode,0,r.stderr)
        d=json.loads(r.stdout)
        self.assertEqual(d['attempts'],0)
        self.assertEqual(d['completionminattempts'],1)
        self.assertEqual(d['completionminattemptsenabled'],1)
        self.assertEqual(d['completionattemptsexhausted'],0)
        self.assertEqual(d['gradepass'],75)
        s['version']=4
        self.assertEqual(self.helper(s).returncode,2)

    def test_conditions_require_existing_previous_targets_and_valid_state(self):
        s=self.spec()
        base=dict(type='completion',activity='pratique',state=1)
        for c in [dict(type='completion',activity='absent'),dict(type='grade',activity='pratique',min=75),
                  dict(type='completion',activity='pratique',state=2),dict(type='date',activity='pratique')]:
            s['conditions']=[c]
            r=self.helper(s,"mcb_valider_conditions((object)['conditions'=>$s->conditions],['pratique'=>$s->sections[0]->activities[1]]);")
            self.assertEqual(r.returncode,2,c)
        s['conditions']=[base,base]
        r=self.helper(s,"mcb_valider_conditions((object)['conditions'=>$s->conditions],['pratique'=>$s->sections[0]->activities[1]]);")
        self.assertEqual(r.returncode,2)

    def test_grade_conditions_remap_grade_item_separately_from_module_id(self):
        s=self.spec()
        code='''define('MUST_EXIST',2);
        class DB {function get_record($t,$args,...$rest){return (object)['id'=>17,'module'=>4,'instance'=>21];}
          function get_field(...$args){return 'quiz';}} $DB=new DB();
        class grade_item {static function fetch($args){return (object)['id'=>910];}}
        $a=(object)['conditions'=>[(object)['type'=>'grade','activity'=>'test','min'=>75],
          (object)['type'=>'completion','activity'=>'pratique','state'=>1]]];
        echo json_encode(mcb_availability_certificat($a,3));'''
        r=self.helper(s,code);self.assertEqual(r.returncode,0,r.stderr)
        d=json.loads(r.stdout)
        self.assertEqual(d['c'],[dict(type='grade',id=910,min=75),dict(type='completion',cm=17,e=1)])
        self.assertEqual(d['showc'],[True,True])

    def test_glossary_verifier_accepts_moodle_string_format_but_rejects_changed_definition(self):
        s=self.spec()
        code='''define('MUST_EXIST',2);define('FORMAT_HTML','1');
        class context_module {static function instance($id){return (object)['id'=>7];}}
        class Portable {function get_content(){return json_encode($GLOBALS['s']->sections[0]->activities[0]->entries);}}
        class Files {function get_file(...$args){return new Portable();}}
        function get_file_storage(){return new Files();}
        class DB {
          function get_record(...$args){return (object)['displayformat'=>'dictionary','assessed'=>'0'];}
          function get_records(...$args){return [(object)['concept'=>'Trace','definition'=>$GLOBALS['changed']?'Wrong':'<p>Production remise.</p>','definitionformat'=>'1','approved'=>'1']];}
        }$DB=new DB();$cm=(object)['id'=>3,'instance'=>9];$GLOBALS['changed']=false;
        $good=mcb_verifier_glossaire($cm,$s->sections[0]->activities[0]);$GLOBALS['changed']=true;
        echo json_encode([$good,mcb_verifier_glossaire($cm,$s->sections[0]->activities[0])]);'''
        r=self.helper(s,code);self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout),[True,False])


    def test_portable_terms_do_not_include_author_or_usage_metadata(self):
        s=self.spec();e=s['sections'][0]['activities'][0]['entries'][0]
        e.update(author='Private metadata',userid=123,attempts=[1,2])
        r=self.helper(s,'echo json_encode(mcb_termes_modele($s->sections[0]->activities[0]->entries));')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout),[dict(concept=e['concept'],definition=e['definition'])])


if __name__=='__main__': unittest.main()
