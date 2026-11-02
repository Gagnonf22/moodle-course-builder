"""Contrat v4 et vérification des sauts ; parcours navigateur éprouvés séparément."""
import base64
import copy
import json
import subprocess
import unittest
import test_moodle_cli as cli


@unittest.skipUnless(cli.PHP, 'PHP_BIN requis')
class ParcoursRetroactionTests(unittest.TestCase):
    setUp=cli.MoodleCliTests.setUp
    run_script=cli.MoodleCliTests.run_script

    def spec(self):
        (self.project/'background.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j2WQAAAAASUVORK5CYII='))
        source=dict(type='h5p',idnumber='evaluation',completion='pass',gradepass=75)
        feedback=dict(type='feedback',idnumber='avis',completion='submit',anonymous=True,items=[
            dict(key='choix',type='multichoice',name='Choisir',required=True,choices=['A','B']),
            dict(key='court',type='textfield',name='Réponse',required=True),
            dict(key='long',type='textarea',name='Détails'),dict(key='info',type='info',name='Cours'),
            dict(key='texte',type='label',name='Explication',html='<p>Fictif</p>')])
        lesson=dict(type='lesson',idnumber='parcours',completion='end',pages=[
            dict(key='a',type='content',title='Départ',html='A',choices=[dict(text='Poursuivre',to='b')]),
            dict(key='b',type='question',title='Question',html='B',choices=[dict(text='Oui',to='END',correct=True),
                dict(text='Non',to='a',correct=False)])])
        cert=dict(type='customcert',idnumber='attestation',completion='view',condition='evaluation',course_required=False,
            certificate=dict(background='background.png',width=297,height=210))
        return dict(version=4,sections=[dict(activities=[source,feedback,lesson,cert])])

    def probe(self,s,code='mcb_valider_structure($s,$p);echo "VALID";'):
        (self.project/'spec.json').write_text(json.dumps(s),encoding='utf8')
        script=self.root/'probe.php'
        script.write_text('<?php require '+json.dumps(str(cli.SCRIPTS/'activites_etendues.php'))+
            ';$p='+json.dumps(str(self.project))+';$s=json_decode(file_get_contents($p."/spec.json"));'+
            'try{'+code+'}catch(InvalidArgumentException $e){fwrite(STDERR,$e->getMessage());exit(2);}',encoding='utf8')
        return subprocess.run([cli.PHP,'-n',str(script)],capture_output=True,text=True,encoding='utf8')

    def test_three_profiles_and_both_anonymity_modes(self):
        for anonymous in [False,True]:
            s=self.spec();s['sections'][0]['activities'][1]['anonymous']=anonymous
            r=self.probe(s);self.assertEqual(r.returncode,0,r.stderr)

    def test_feedback_required_info_duplicate_and_unknown_refused(self):
        for mode in ['required-info','duplicate','unknown','bad-anonymous','choice-separator']:
            s=self.spec();f=s['sections'][0]['activities'][1]
            if mode=='required-info':f['items'][3]['required']=True
            elif mode=='duplicate':f['items'][1]['key']='choix'
            elif mode=='unknown':f['items'][1]['type']='rating'
            elif mode=='bad-anonymous':f['anonymous']='yes'
            else:f['items'][0]['choices']=['A|B','C']
            self.assertEqual(self.probe(s).returncode,2,mode)

    def test_feedback_mapping_and_single_response_settings(self):
        s=self.spec()
        code='''function file_get_unused_draft_itemid(){return 1;}
        $a=$s->sections[0]->activities[1];$mi=new stdClass();mcb_preparer_parcours($mi,$a);
        echo json_encode([$mi,mcb_item_feedback($a->items[0],19,1),mcb_item_feedback($a->items[2],19,3)]);'''
        r=self.probe(s,code);self.assertEqual(r.returncode,0,r.stderr)
        module,choice,long=json.loads(r.stdout)
        self.assertEqual(module['anonymous'],1);self.assertEqual(module['multiple_submit'],0)
        self.assertEqual(module['completionsubmit'],1)
        self.assertEqual(choice['presentation'],'r>>>>>A|B');self.assertEqual(long['required'],0)

    def test_lesson_jumps_require_keys_and_end_reachability(self):
        for destination in [123,'absente']:
            s=self.spec();s['sections'][0]['activities'][2]['pages'][0]['choices'][0]['to']=destination
            self.assertEqual(self.probe(s).returncode,2)
        s=self.spec();s['sections'][0]['activities'][2]['pages'][1]['choices'][0]['to']='a'
        self.assertEqual(self.probe(s).returncode,2)

    def test_lesson_duplicates_and_question_correctness_refused(self):
        for mode in ['duplicate','zero-correct','two-correct']:
            s=self.spec();pages=s['sections'][0]['activities'][2]['pages']
            if mode=='duplicate':pages[1]['key']='a'
            elif mode=='zero-correct':pages[1]['choices'][0]['correct']=False
            else:pages[1]['choices'][1]['correct']=True
            self.assertEqual(self.probe(s).returncode,2)

    def test_certificate_dependency_must_precede_and_require_success(self):
        for mode in ['absent','after','not-pass','state','criterion']:
            s=self.spec();acts=s['sections'][0]['activities'];c=acts[-1]
            if mode=='absent':c['condition']='absent'
            elif mode=='after':acts[:]=[c,*acts[:-1]]
            elif mode=='not-pass':acts[0]['completion']='view'
            elif mode=='state':c['condition_state']=0
            else:c['course_required']=True
            self.assertEqual(self.probe(s).returncode,2)

    def test_certificate_background_and_dimensions_validated(self):
        for filename in ['missing.png','../outside.png']:
            (self.root/'outside.png').write_bytes((self.project/'background.png').read_bytes()) if (self.project/'background.png').exists() else None
            s=self.spec();s['sections'][0]['activities'][-1]['certificate']['background']=filename
            self.assertEqual(self.probe(s).returncode,2)
        s=self.spec();(self.project/'background.png').write_text('not PNG',encoding='utf8')
        self.assertEqual(self.probe(s).returncode,2)
        s=self.spec();s['sections'][0]['activities'][-1]['certificate']['width']=0
        self.assertEqual(self.probe(s).returncode,2)

    def test_end_completion_not_allowed_on_another_module(self):
        s=self.spec();s['sections'][0]['activities'][0]['completion']='end'
        self.assertEqual(self.probe(s).returncode,2)

    def test_verifier_handles_string_ids_and_rejects_wrong_jump(self):
        s=self.spec()
        code=r'''
        define('MUST_EXIST',2);
        class DB {
          function get_record($table,$args,...$rest){return (object)['completionendreached'=>1,'grade'=>0,'practice'=>1];}
          function get_records($table,$args,...$rest){
            if($table==='lesson_pages'){return [31=>(object)['id'=>'31','prevpageid'=>'0','nextpageid'=>'32','qtype'=>'20','title'=>'Départ','contents'=>'A'],
             32=>(object)['id'=>'32','prevpageid'=>'31','nextpageid'=>'0','qtype'=>'3','title'=>'Question','contents'=>'B']];}
            if($args['pageid']==31){return [(object)['answer'=>'Poursuivre','response'=>'','jumpto'=>'32','score'=>'0']];}
            return [(object)['answer'=>'Oui','response'=>'','jumpto'=>'-9','score'=>'1'],
              (object)['answer'=>'Non','response'=>'','jumpto'=>getenv('WRONG_JUMP') ?: '31','score'=>'0']];
          }
        }
        $DB=new DB();$a=$s->sections[0]->activities[2];
        if(!mcb_verifier_parcours((object)['instance'=>7],$a,$p)){exit(1);}
        putenv('WRONG_JUMP=999');
        if(mcb_verifier_parcours((object)['instance'=>7],$a,$p)){exit(1);}
        echo 'VALID';
        '''
        r=self.probe(s,code);self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_old_versions_do_not_create_new_profiles(self):
        for version in [1,2,3]:
            s=self.spec();s['version']=version
            (self.project/'cours/structure.json').write_text(json.dumps(s),encoding='utf8')
            r=self.run_script('construire_cours.php','--validation-locale')
            self.assertEqual(r.returncode,2,r.stdout+r.stderr)
            self.assertNotIn('UNEXPECTED_CREATE',r.stdout+r.stderr)

    def test_invalid_graph_cli_does_not_create(self):
        s=self.spec();s['sections'][0]['activities'][2]['pages'][0]['choices'][0]['to']='unknown'
        (self.project/'cours/structure.json').write_text(json.dumps(s),encoding='utf8')
        r=self.run_script('construire_cours.php','--validation-locale')
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        self.assertNotIn('UNEXPECTED_CREATE',r.stdout+r.stderr)


if __name__=='__main__':unittest.main()
