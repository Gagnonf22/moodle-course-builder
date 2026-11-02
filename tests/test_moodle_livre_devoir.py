"""Contrat v2 et appels aux contrôleurs, sans prétendre remplacer l'essai Moodle."""
import copy
import json
import os
from pathlib import Path
import subprocess
import unittest
import test_moodle_cli as cli


@unittest.skipUnless(cli.PHP, 'PHP_BIN requis')
class LivreDevoirTests(unittest.TestCase):
    setUp = cli.MoodleCliTests.setUp
    run_script = cli.MoodleCliTests.run_script

    def spec(self):
        (self.project/'chapter.html').write_text('<p>Fictif</p>', encoding='utf8')
        return dict(version=2, sections=[dict(activities=[dict(type='book', idnumber='b',
            completion='view', chapters=[dict(title='Titre', html='chapter.html')]),
            dict(type='assign', idnumber='a', completion='pass', grade=100, gradepass=75,
                submission=dict(text=True, files=False), grading=dict(method='rubric', name='Grille',
                    criteria=[dict(description='Exactitude', levels=[dict(score=0, definition='Absent'),
                        dict(score=2, definition='Exact')])]))])])

    def helper(self, spec, code='mcb_valider_structure($s,$p); echo "VALID";'):
        (self.project/'spec.json').write_text(json.dumps(spec), encoding='utf8')
        script=self.root/'probe.php'
        script.write_text('<?php\nrequire '+json.dumps(str(cli.SCRIPTS/'activites_etendues.php'))+
            '; $p='+json.dumps(str(self.project))+'; $s=json_decode(file_get_contents($p."/spec.json"));\n'+
            'try {'+code+'} catch (InvalidArgumentException $e) {fwrite(STDERR,$e->getMessage());exit(2);}', encoding='utf8')
        return subprocess.run([cli.PHP,'-n',str(script)],capture_output=True,text=True,encoding='utf8')

    def test_valid_rubric_and_guide_and_all_submission_modes(self):
        for method in ['rubric','guide']:
            for text,files in [(True,False),(False,True),(True,True)]:
                s=self.spec(); a=s['sections'][0]['activities'][1]
                a['submission']=dict(text=text,files=files)
                if method=='guide': a['grading']=dict(method='guide',name='Guide',criteria=[dict(description='Exactitude',maxscore=5)])
                r=self.helper(s)
                self.assertEqual(r.returncode,0,r.stderr)

    def test_invalid_version_and_duplicate_keys_are_refused_before_create(self):
        for version in [1,999,'2']:
            s=self.spec(); s['version']=version
            self.assertEqual(self.helper(s).returncode,2)
        s=self.spec(); s['sections'][0]['activities'][1]['idnumber']='b'
        self.assertEqual(self.helper(s).returncode,2)

    def test_chapter_file_escape_and_missing_and_first_subchapter_refused(self):
        for path in ['missing.html','../outside.html']:
            (self.root/'outside.html').write_text('Outside',encoding='utf8')
            s=self.spec(); s['sections'][0]['activities'][0]['chapters'][0]['html']=path
            self.assertEqual(self.helper(s).returncode,2)
        s=self.spec(); s['sections'][0]['activities'][0]['chapters'][0]['subchapter']=True
        self.assertEqual(self.helper(s).returncode,2)

    def test_bad_submission_and_pass_threshold_refused(self):
        for change in [dict(submission=dict(text=False,files=False)), dict(submission=dict(text='yes')),
                       dict(gradepass=101),dict(gradepass=0),dict(grade=-1),
                       dict(submission=dict(text=True,maxfiles=0)), dict(completion='view')]:
            s=self.spec(); s['sections'][0]['activities'][1].update(change)
            self.assertEqual(self.helper(s).returncode,2,change)

    def test_rubric_cannot_silently_drop_levels_or_zero(self):
        for levels in [[dict(score=2,definition='Unique')],
                       [dict(score=1,definition='A'),dict(score=2,definition='B')],
                       [dict(score=0,definition='A'),dict(score=0,definition='B')]]:
            s=self.spec(); s['sections'][0]['activities'][1]['grading']['criteria'][0]['levels']=levels
            self.assertEqual(self.helper(s).returncode,2)

    def test_assignment_preparation_preserves_submission_and_grade_contract(self):
        code='''mcb_valider_structure($s,$p); $a=$s->sections[0]->activities[1];
        $mi=new stdClass(); mcb_preparer_devoir($mi,$a); echo json_encode($mi);'''
        r=self.helper(self.spec(),code); self.assertEqual(r.returncode,0,r.stderr)
        fields=json.loads(r.stdout)
        self.assertEqual(fields['gradepass'],75)
        self.assertEqual(fields['assignsubmission_onlinetext_enabled'],1)
        self.assertEqual(fields['assignsubmission_file_enabled'],0)
        self.assertEqual(fields['advancedgradingmethod_submissions'],'rubric')
        self.assertEqual(fields['completionsubmit'],0)
        self.assertEqual(fields['sendstudentnotifications'],0)

    def test_controller_receives_ready_definition_and_chapters(self):
        code=r'''
        define('FORMAT_HTML',1);
        class context_module {static function instance($id){return (object)['id'=>$id];}}
        class gradingform_controller {const DEFINITION_STATUS_READY=20;}
        class Manager {
          function set_active_method($x){}
          function get_controller($x){return $this;}
          function update_definition($x){echo json_encode($x);}
        }
        function get_grading_manager(...$args){return new Manager();}
        function file_get_unused_draft_itemid(){return 1;}
        eval('namespace mod_book\\event; class chapter_created {static function create_from_chapter(...$args){return new self();} function trigger(){}}');
        function book_preload_chapters($book){$GLOBALS['preloaded']=true;}
        define('MUST_EXIST',2);
        class DB {
          function insert_record($table,$row){$GLOBALS['rows'][]=$row;return 7;}
          function get_record(...$args){return (object)['id'=>17,'revision'=>0];}
          function set_field($table,$field,$value,$args){$GLOBALS['revision']=$value;}
        }
        $DB=new DB(); $CFG=(object)['dirroot'=>$p];
        $cm=(object)['instance'=>17,'coursemodule'=>23];
        mcb_finaliser_activite($cm,$s->sections[0]->activities[0],$p);
        if ($GLOBALS['rows'][0]->content!=='<p>Fictif</p>' || $GLOBALS['rows'][0]->bookid!==17 ||
            $GLOBALS['revision']!==1 || !$GLOBALS['preloaded']) {exit(1);}
        mcb_finaliser_activite($cm,$s->sections[0]->activities[1],$p);
        '''
        (self.project/'grade/grading').mkdir(parents=True)
        (self.project/'grade/grading/lib.php').write_text('<?php',encoding='utf8')
        (self.project/'mod/book').mkdir(parents=True)
        (self.project/'mod/book/locallib.php').write_text('<?php',encoding='utf8')
        r=self.helper(self.spec(),code); self.assertEqual(r.returncode,0,r.stderr)
        data=json.loads(r.stdout)
        self.assertEqual(data['status'],20)
        self.assertEqual(len(data['rubric']['criteria']['NEWID1']['levels']),2)

    def test_v2_invalid_contract_cli_does_not_create_or_elevate(self):
        s=self.spec(); s['sections'][0]['activities'][1]['gradepass']=200
        (self.project/'cours/structure.json').write_text(json.dumps(s),encoding='utf8')
        r=self.run_script('construire_cours.php','--validation-locale')
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        self.assertNotIn('UNEXPECTED_CREATE',r.stdout+r.stderr)


if __name__=='__main__': unittest.main()
