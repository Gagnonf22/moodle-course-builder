"""Contrat et traduction des questions natives ; essais Moodle documentés séparément."""
import copy
import json
import subprocess
import unittest
import test_moodle_cli as cli


@unittest.skipUnless(cli.PHP, 'PHP_BIN requis')
class TestsNatifsTests(unittest.TestCase):
    setUp = cli.MoodleCliTests.setUp
    run_script = cli.MoodleCliTests.run_script

    def spec(self):
        questions=[dict(key='u',type='multichoice',name='Unique',text='Choisir',mark=1,single=True,
            answers=[dict(text='A',fraction=1,feedback='Oui'),dict(text='B',fraction=0,feedback='Non')]),
            dict(key='m',type='multichoice',name='Multiple',text='Choisir deux',mark=2,single=False,
            answers=[dict(text='A',fraction=.5),dict(text='B',fraction=.5),dict(text='C',fraction=-1)]),
            dict(key='t',type='truefalse',name='Faux',text='Affirmation',mark=1,correct=False,feedbacktrue='Non',feedbackfalse='Oui'),
            dict(key='s',type='shortanswer',name='Mot',text='Écrire',mark=1,usecase=False,
            answers=[dict(text='mot',fraction=1),dict(text='*',fraction=0)]),
            dict(key='n',type='numerical',name='Mesure',text='Calculer',mark=2,
            answers=[dict(text='10',fraction=1,tolerance=.5,feedback='Tolérance')])]
        bank=dict(type='qbank',idnumber='banque',name='Banque',completion='none',course_required=False,questions=questions)
        quiz=dict(type='quiz',idnumber='test',name='Test',completion='pass',bank='banque',questions=['u','m','t','s','n'],
            grade=100,gradepass=75,attempts=2,grademethod='highest',review=dict(during=dict(attempt=True),
            immediately=dict(attempt=True,marks=True,generalfeedback=True)))
        return dict(version=3,sections=[dict(activities=[bank,quiz])])

    def probe(self,s,code='mcb_valider_structure($s,$p);echo "VALID";'):
        (self.project/'spec.json').write_text(json.dumps(s),encoding='utf8')
        script=self.root/'probe.php'
        script.write_text('<?php require '+json.dumps(str(cli.SCRIPTS/'activites_etendues.php'))+
            ';$p='+json.dumps(str(self.project))+';$s=json_decode(file_get_contents($p."/spec.json"));'+
            'try{'+code+'}catch(InvalidArgumentException $e){fwrite(STDERR,$e->getMessage());exit(2);}',encoding='utf8')
        return subprocess.run([cli.PHP,'-n',str(script)],capture_output=True,text=True,encoding='utf8')

    def test_four_types_and_both_choice_modes_validate(self):
        r=self.probe(self.spec());self.assertEqual(r.returncode,0,r.stderr)

    def test_distributed_example_validates(self):
        s=json.loads((cli.SCRIPTS.parents[1]/'assets/exemple-test-natif.json').read_text(encoding='utf8'))
        r=self.probe(s);self.assertEqual(r.returncode,0,r.stderr)

    def test_bank_can_have_unused_questions(self):
        s=self.spec();s['sections'][0]['activities'][1]['questions']=['n']
        r=self.probe(s);self.assertEqual(r.returncode,0,r.stderr)

    def test_old_contract_refuses_native_bank(self):
        for version in [1,2]:
            s=self.spec();s['version']=version
            self.assertEqual(self.probe(s).returncode,2)

    def test_unknown_question_type_is_not_converted(self):
        s=self.spec();s['sections'][0]['activities'][0]['questions'][0]['type']='calculated'
        self.assertEqual(self.probe(s).returncode,2)

    def test_duplicate_question_keys_and_unknown_references_refused(self):
        for mode in ['duplicate-key','unknown-ref','duplicate-ref','bank-after-test']:
            s=self.spec();bank,quiz=s['sections'][0]['activities']
            if mode=='duplicate-key':bank['questions'][1]['key']='u'
            elif mode=='unknown-ref':quiz['questions'][0]='absente'
            elif mode=='duplicate-ref':quiz['questions'][1]='u'
            else:s['sections'][0]['activities']=[quiz,bank]
            self.assertEqual(self.probe(s).returncode,2,mode)

    def test_multiple_choice_incoherent_fractions_refused(self):
        for fractions in [[.5,.25,-1],[1,1,-1],[.5,.5,-2]]:
            s=self.spec();q=s['sections'][0]['activities'][0]['questions'][1]
            for answer,fraction in zip(q['answers'],fractions):answer['fraction']=fraction
            self.assertEqual(self.probe(s).returncode,2)
        s=self.spec();s['sections'][0]['activities'][0]['questions'][0]['answers'][1]['fraction']=1
        self.assertEqual(self.probe(s).returncode,2)

    def test_numerical_tolerance_and_mark_validated(self):
        for field,value in [('tolerance',-.1),('tolerance','0.5'),('text','abc')]:
            s=self.spec();s['sections'][0]['activities'][0]['questions'][-1]['answers'][0][field]=value
            self.assertEqual(self.probe(s).returncode,2)
        s=self.spec();s['sections'][0]['activities'][0]['questions'][-1]['mark']=0
        self.assertEqual(self.probe(s).returncode,2)

    def test_review_unknown_or_ambiguous_options_refused(self):
        for review in [dict(during=dict(attempt=False)),dict(during=dict(attempt=True,overallfeedback=True)),
                       dict(during=dict(attempt=True),later=dict(marks=True)),dict(during=dict(attempt=True),open=dict(marks='yes'))]:
            s=self.spec();s['sections'][0]['activities'][1]['review']=review
            self.assertEqual(self.probe(s).returncode,2)

    def test_quiz_attempts_grade_and_bank_completion_refused(self):
        for field,value in [('attempts',0),('attempts','2'),('grademethod','mystery'),('gradepass',101),('gradepass',0)]:
            s=self.spec();s['sections'][0]['activities'][1][field]=value
            self.assertEqual(self.probe(s).returncode,2)
        s=self.spec();s['sections'][0]['activities'][0]['completion']='view'
        self.assertEqual(self.probe(s).returncode,2)

    def test_form_preserves_negative_fraction_tolerance_and_false_feedback(self):
        code='echo json_encode(array_map(fn($q)=>mcb_form_question($q,123),$s->sections[0]->activities[0]->questions));'
        r=self.probe(self.spec(),code);self.assertEqual(r.returncode,0,r.stderr)
        forms=json.loads(r.stdout)
        self.assertEqual(forms[1]['fraction'],[.5,.5,-1])
        self.assertEqual(forms[2]['correctanswer'],0)
        self.assertEqual(forms[2]['feedbackfalse']['text'],'Oui')
        self.assertEqual(forms[4]['tolerance'],['0.5'])
        self.assertEqual(forms[4]['feedback'][0]['text'],'Tolérance')

    def test_grading_methods_and_review_fields_preserved(self):
        for name,number in [('highest',1),('average',2),('first',3),('last',4)]:
            s=self.spec();s['sections'][0]['activities'][1]['grademethod']=name
            r=self.probe(s,'$mi=new stdClass();mcb_preparer_test($mi,$s->sections[0]->activities[1]);echo json_encode($mi);')
            self.assertEqual(r.returncode,0,r.stderr);form=json.loads(r.stdout)
            self.assertEqual(form['grademethod'],number)
            self.assertEqual(form['marksimmediately'],1)
            self.assertEqual(form['rightanswerimmediately'],0)
            self.assertEqual(form['gradepass'],75)

    def test_invalid_question_cli_refuses_before_course_creation(self):
        s=self.spec();s['sections'][0]['activities'][0]['questions'][0]['type']='not-supported'
        (self.project/'cours/structure.json').write_text(json.dumps(s),encoding='utf8')
        r=self.run_script('construire_cours.php','--validation-locale')
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        self.assertNotIn('UNEXPECTED_CREATE',r.stdout+r.stderr)


if __name__=='__main__':unittest.main()
