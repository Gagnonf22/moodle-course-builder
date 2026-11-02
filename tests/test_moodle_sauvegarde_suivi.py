"""Contrats CLI et issues négatives sur doublures ; aucune API Moodle exécutée."""
import json
from pathlib import Path
import unittest

import test_moodle_cli as cli
PHP, CONFIG = cli.PHP, cli.CONFIG

EXTRA = r'''
namespace core_availability {
 class info_module {
  function __construct($cm) {}
  function is_available(&$why,$all=false,$uid=0) { return getenv('BAD_ACCESS') === '1' || $uid===12; }
 }
}
namespace {
class SyntheticPackage {
 function get_contenthash() { return sha1('fake-h5p'); }
 function get_filesize() { return 8; }
}
class grade_item { static function fetch($args) { return (object)['grademax'=>100, 'gradepass'=>70]; } }
function is_enrolled(...$args) { return getenv('NOT_ENROLLED') !== '1'; }
function is_siteadmin($id) { return getenv('ADMIN_PROBE') === '1'; }
function has_capability(...$args) { return false; }
class base_setting { const NOT_LOCKED=0; }
class FakeSetting {
 public $name; public $value;
 function __construct($name) { $this->name=$name; $this->value=$name==='filename' ? 'native.mbz' : (in_array($name,['files','contentbankcontent']) ? 0 : 1); }
 function get_status() { return getenv('LOCKED_SETTING')===$this->name ? 1 : 0; }
 function set_value($value) { $this->value=$value; }
 function get_value() { return $this->value; }
}
class FakePlan {
 public $settings=[];
 function setting_exists($name) { return !(getenv('MISSING_USERS')==='1' && $name==='users'); }
 function get_setting($name) { return $this->settings[$name] ??= new FakeSetting($name); }
}
class backup { const TYPE_1COURSE=1,FORMAT_MOODLE=1,INTERACTIVE_NO=0,MODE_GENERAL=1; }
class NativeFile {
 function get_content_file_handle() { $h=fopen('php://temp','w+b'); fwrite($h,'NATIVE-FAKE'); rewind($h); return $h; }
 function get_filesize() { return getenv('BAD_COPY')==='1' ? '500' : '11'; }
}
class backup_controller {
 public $plan;
 function __construct(...$args) { $this->plan=new FakePlan(); }
 function get_plan() { return $this->plan; }
 function execute_plan() {
  if ($this->plan->get_setting('users')->get_value()!==0) { throw new \Exception('UNEXPECTED_USERDATA'); }
  foreach (['files','contentbankcontent'] as $name) {
   if ($this->plan->get_setting($name)->get_value()!==1) { throw new \Exception('MISSING_REQUIRED_CONTENT:'.$name); }
  }
  if (getenv('EXEC_FAIL')==='1') { throw new \Exception('FAKE_BACKUP_FAILURE'); }
 }
 function get_results() { return ['backup_destination'=>new NativeFile()]; }
 function destroy() {}
}
}
'''


@unittest.skipUnless(PHP, 'PHP CLI absent ; définir PHP_BIN')
class SauvegardeSuiviTests(unittest.TestCase):
    setUp = cli.MoodleCliTests.setUp
    run_script = cli.MoodleCliTests.run_script

    def prepare(self):
        config = CONFIG.replace("return $table==='course' ? (object)['id'=>99] : (object)['content'=>str_repeat('x',201)];", """
if ($table==='course_modules_completion') { return (object)['completionstate'=>getenv('BAD_STATE')==='1' ? 0 : ($args['userid']===11 ? 3 : 2)]; }
if ($table==='feedback') { return (object)['completionsubmit'=>getenv('BAD_SUBMIT')==='1' ? 0 : 1]; }
return $table==='course' ? (object)['id'=>99] : (object)['content'=>str_repeat('x',201)];""")
        config = config.replace("return $component==='course' ? [(object)[]] : [];", "return $component==='course' ? [(object)[]] : ($component==='mod_h5pactivity' ? [new SyntheticPackage()] : []);")
        config = config.replace("return 1; }", "return getenv('HAS_SPEC')==='1' ? 2 : 1; }")
        start = config.index('class Modinfo {')
        end = config.index('function get_fast_modinfo', start)
        config = config[:start] + r'''
class Modinfo {
 public $cms; public $sections;
 function __construct() {
  $this->cms=[];
  foreach (json_decode(getenv('MODULES') ?: '[]') as $cm) { $this->cms[$cm->id]=$cm; }
  $this->sections=[0=>array_keys($this->cms)];
 }
 function get_section_info($num) { return (object)['name'=>'Section']; }
 function get_cm($id) { return $this->cms[$id]; }
}
''' + config[end:]
        (self.moodle/'config.php').write_text(config+EXTRA, encoding='utf8')
        f=self.moodle/'backup/util/includes/backup_includes.php'
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text('<?php\n',encoding='utf8')

    def backup(self, **env):
        self.prepare()
        out=self.root/'export.mbz'
        result=self.run_script('sauvegarder_cours.php','--validation-locale','--courseid=1',f'--fichier={out}',**env)
        return result,out

    def test_native_backup_new_output_and_no_userdata(self):
        result,out=self.backup()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(out.read_bytes(),b'NATIVE-FAKE')
        result=self.run_script('sauvegarder_cours.php','--validation-locale','--courseid=1',f'--fichier={out}')
        self.assertEqual(result.returncode,2)
        self.assertEqual(out.read_bytes(),b'NATIVE-FAKE')

    def test_native_backup_refusals_and_partial_output_cleanup(self):
        for env in ({'MISSING_USERS':'1'},{'LOCKED_SETTING':'users'}, {'LOCKED_SETTING':'comments'},
                    {'BAD_COPY':'1'}, {'EXEC_FAIL':'1'}, {'TEST_DBHOST':'"remote.invalid"'}):
            with self.subTest(env=env):
                result,out=self.backup(**env)
                self.assertEqual(result.returncode,2,result.stdout+result.stderr)
                self.assertFalse(out.exists())

    def test_native_backup_requires_assertion_before_bootstrap(self):
        (self.moodle/'config.php').write_text('BOOTSTRAP_MUST_NOT_RUN',encoding='utf8')
        r=self.run_script('sauvegarder_cours.php','--courseid=1',f'--fichier={self.root/"x.mbz"}')
        self.assertEqual(r.returncode,2)
        self.assertNotIn('BOOTSTRAP_MUST_NOT_RUN',r.stdout)

    def test_native_backup_locked_files_or_contentbank_refused(self):
        for setting in ('files','contentbankcontent'):
            with self.subTest(setting=setting):
                r,out=self.backup(LOCKED_SETTING=setting)
                self.assertEqual(r.returncode,2,r.stdout+r.stderr)
                self.assertIn('Contenu désactivé : '+setting,r.stderr)
                self.assertFalse(out.exists())

    def specification(self, kind='feedback', condition_state=1):
        (self.project/'final.h5p').write_bytes(b'fake-h5p')
        acts=[dict(type='h5p', name='Final', idnumber='final',completion='pass',package='final.h5p',gradepass=70),
              dict(type='customcert',name='Recognition',idnumber='recognition',completion='view',
                   condition='final',course_required=False),
              dict(type=kind,name='Feedback',idnumber='feedback',completion='submit' if kind=='feedback' else 'manual')]
        if condition_state is not None:
            acts[1]['condition_state']=condition_state
        spec=dict(version=1,sections=[dict(name='Section',activities=acts)])
        (self.project/'cours/structure.json').write_text(json.dumps(spec),encoding='utf8')
        cms=[]
        for i,a in enumerate(acts,1):
            cms.append(dict(id=i,instance=i,modname='h5pactivity' if a['type']=='h5p' else a['type'],idnumber=a['idnumber'],name=a['name'],
                completion=1 if a['completion']=='manual' else 2,completionview=int(a['completion']=='view'),
                completiongradeitemnumber=0,completionpassgrade=int(i==1),
                availability=json.dumps(dict(op='&',c=[dict(type='completion',cm=1,e=condition_state or 1)],showc=[True])) if i==2 else None))
        return dict(MODULES=json.dumps(cms),HAS_SPEC='1')

    def verify(self, kind='feedback', probes=True, condition_state=1, **env):
        self.prepare()
        base=self.specification(kind,condition_state)
        args=[]
        if probes:
            p=self.root/'apprenants.json'; p.write_text(json.dumps(dict(echec=11,reussite=12)),encoding='utf8')
            args=[f'--apprenants={p}']
        return self.run_script('verifier_cours.php','--courseid=1',*args,**base,**env)

    def test_certificate_both_access_states_and_feedback_submission(self):
        r=self.verify()
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertIn('attestation echec : restriction',r.stdout)
        self.assertIn('attestation reussite : restriction',r.stdout)

    def test_certificate_default_matches_generator_and_explicit_pass_supported(self):
        for state in (None,2):
            with self.subTest(condition_state=state):
                r=self.verify(condition_state=state)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_certificate_missing_probes_is_incomplete_not_success(self):
        r=self.verify(probes=False)
        self.assertEqual(r.returncode,1,r.stdout+r.stderr)
        self.assertIn('compte d’essai distinct manquant',r.stdout)

    def test_access_state_privileged_unenrolled_and_feedback_negative_paths(self):
        for env in ({'BAD_ACCESS':'1'},{'BAD_STATE':'1'},{'ADMIN_PROBE':'1'},
                    {'NOT_ENROLLED':'1'},{'BAD_SUBMIT':'1'}):
            with self.subTest(env=env):
                r=self.verify(**env)
                self.assertEqual(r.returncode,1,r.stdout+r.stderr)

    def test_questionnaire_is_a_separate_type(self):
        r=self.verify(kind='questionnaire')
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_unsupported_generation_is_refused_before_create(self):
        self.specification()
        r=self.run_script('construire_cours.php','--validation-locale')
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        self.assertIn('type non fabriqué',r.stderr)


if __name__=='__main__': unittest.main()
