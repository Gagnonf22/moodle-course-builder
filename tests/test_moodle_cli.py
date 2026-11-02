"""Exécuter les scripts PHP avec une doublure minimale de Moodle, sans DB.

PHP_BIN permet de désigner un PHP CLI portable. Une doublure teste les branches
visées ; elle ne démontre pas la compatibilité des API ni une restauration.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PHP = os.environ.get('PHP_BIN') or shutil.which('php')
SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts/moodle'

CONFIG = r'''<?php
namespace core\session { class manager { static function set_user($x) {} } }
namespace {
$CFG = (object)['libdir' => __DIR__.'/lib', 'dirroot' => __DIR__, 'wwwroot' => getenv('TEST_WWWROOT') ?: 'http://localhost'];
if (getenv('TEST_DBHOST_MISSING') !== '1') {
 $CFG->dbhost = getenv('TEST_DBHOST') !== false ? json_decode(getenv('TEST_DBHOST')) : 'localhost';
}
$CFG->dboptions = ['dbsocket' => getenv('TEST_DBSOCKET') !== false ? json_decode(getenv('TEST_DBSOCKET')) : false];
$USER = (object)['id' => 1];
define('COMPLETION_CRITERIA_TYPE_ACTIVITY', 1);
class context_user { static function instance($x) { return (object)['id'=>1]; } }
class context_course { static function instance($x) { return (object)['id'=>1]; } }
class context_module { static function instance($x) { return (object)['id'=>1]; } }
function get_admin() { return (object)['id'=>1]; }
function get_course($x) { return (object)['id'=>1,'fullname'=>'Test','shortname'=>'test','format'=>'topics','visible'=>0,'enablecompletion'=>1]; }
class Files { function get_area_files($ctx,$component,$area,...$args) { return $component==='course' ? [(object)[]] : []; } }
function get_file_storage() { return new Files(); }
class DB {
 function get_record($table, $args) { return $table==='course' ? (object)['id'=>99] : (object)['content'=>str_repeat('x',201)]; }
 function count_records(...$x) { return 1; }
 function count_records_sql(...$x) { return 0; }
}
$DB = new DB();
function create_course($x) { throw new \Exception('UNEXPECTED_CREATE'); }
function delete_course(...$x) { throw new \Exception('UNEXPECTED_DELETE'); }
class Modinfo {
 public $cms; public $sections;
 function __construct() {
  $item = json_decode(getenv('TEST_ITEM') ?: '0');
  $this->cms=[1=>(object)['id'=>1,'modname'=>'page','name'=>'Activity','completion'=>(int)getenv('TEST_COMPLETION'),'completiongradeitemnumber'=>$item,'completionpassgrade'=>0]];
  $this->sections=[0=>[1]];
 }
 function get_section_info($num) { return (object)['name'=>'Section']; }
}
function get_fast_modinfo($x) { return new Modinfo(); }
}
'''


@unittest.skipUnless(PHP, 'PHP CLI absent ; définir PHP_BIN pour ces contrôles')
class MoodleCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mcbp-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.moodle = self.root / 'm'
        self.project = self.root / 'p'
        self.moodle.mkdir()
        (self.moodle / 'config.php').write_text(CONFIG, encoding='utf-8')
        for name in ('lib/clilib.php', 'lib/gradelib.php', 'lib/completionlib.php', 'course/lib.php',
                     'course/modlib.php', 'completion/criteria/completion_criteria_activity.php',
                     'completion/completion_aggregation.php', 'lib/resourcelib.php'):
            f = self.moodle / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text('<?php\n', encoding='utf-8')
        (self.project / 'cours').mkdir(parents=True)
        spec = {'shortname':'test','sections':[{'name':'Section','activities':[
            {'name':'Activity','type':'page','completion':'grade'}]}]}
        (self.project / 'cours/structure.json').write_text(json.dumps(spec), encoding='utf-8')

    def run_script(self, name, *args, **env):
        if name == 'verifier_cours.php':
            args = (*args, '--validation-locale')
        return subprocess.run([PHP, '-n', str(SCRIPTS / name), f'--moodle={self.moodle}',
                               f'--projet={self.project}', *args],
                              capture_output=True, text=True, encoding='utf-8',
                              env={**os.environ, **env})

    def test_php_syntax(self):
        for script in SCRIPTS.glob('*.php'):
            result = subprocess.run([PHP, '-n', '-l', str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_constructor_requires_local_assertion_before_bootstrap(self):
        # Même un config.php invalide ne doit pas être chargé sans l'option.
        (self.moodle / 'config.php').write_text('INVALID CONFIG', encoding='utf-8')
        result = self.run_script('construire_cours.php')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn('INVALID CONFIG', result.stdout)

    def test_constructor_rejects_remote_wwwroot(self):
        result = self.run_script('construire_cours.php', '--validation-locale', TEST_WWWROOT='https://example.invalid')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('Instance refusée', result.stderr)

    def test_collision_refused_without_create_or_delete(self):
        result = self.run_script('construire_cours.php', '--validation-locale')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('Construction refusée', result.stderr)
        self.assertNotIn('UNEXPECTED_', result.stdout + result.stderr)

    def test_constructor_rejects_remote_missing_or_invalid_db_before_admin(self):
        # Si le garde-fou est franchi, cette doublure rend l'élévation visible.
        config = CONFIG.replace('static function set_user($x) {}', "static function set_user($x) { throw new \\Exception('UNEXPECTED_ADMIN'); }")
        (self.moodle / 'config.php').write_text(config, encoding='utf-8')
        cases = [{'TEST_DBHOST': json.dumps(host)} for host in
                 ('db.example.invalid', '192.0.2.1', 'localhost.example.invalid', '', None, 123, 'localhost:3306', '/tmp/mysql.sock')]
        cases.append({'TEST_DBHOST_MISSING': '1'})
        cases.append({'TEST_DBHOST': json.dumps('db.example.invalid'), 'TEST_DBSOCKET': 'true'})
        for env in cases:
            with self.subTest(env=env):
                result = self.run_script('construire_cours.php', '--validation-locale', **env)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('Base refusée', result.stderr)
                self.assertNotIn('UNEXPECTED_', result.stdout + result.stderr)

    def test_constructor_local_db_and_unix_socket_reach_collision_guard(self):
        cases = [{'TEST_DBHOST': json.dumps(host)} for host in ('localhost', '127.0.0.1', '::1', '[::1]')]
        cases += [{'TEST_DBHOST': '"localhost"', 'TEST_DBSOCKET': json.dumps(sock)}
                  for sock in (True, '/var/run/mysqld/mysqld.sock')]
        for env in cases:
            with self.subTest(env=env):
                result = self.run_script('construire_cours.php', '--validation-locale', **env)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('Construction refusée', result.stderr)
                self.assertNotIn('UNEXPECTED_', result.stdout + result.stderr)

    def test_constructor_rejects_invalid_or_nonlocal_socket(self):
        for sock in ('//server/socket', 'relative.sock', '\\\\server\\pipe', 42, '/tmp/a\x00sock'):
            result = self.run_script('construire_cours.php', '--validation-locale', TEST_DBSOCKET=json.dumps(sock))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn('Base refusée', result.stderr)
        result = self.run_script('construire_cours.php', '--validation-locale', TEST_DBHOST='"127.0.0.1"', TEST_DBSOCKET='true')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('socket exige', result.stderr)

    def test_verifier_preserves_failure_for_integer_and_string_zero(self):
        for value in ('0', '"0"'):
            result = self.run_script('verifier_cours.php', '--courseid=1', TEST_COMPLETION='0', TEST_ITEM=value)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('1 échec(s)', result.stdout)

    def test_verifier_success_and_invalid_grade_item(self):
        for value in ('0', '"0"'):
            result = self.run_script('verifier_cours.php', '--courseid=1', TEST_COMPLETION='2', TEST_ITEM=value)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for value in ('1', 'null'):
            result = self.run_script('verifier_cours.php', '--courseid=1', TEST_COMPLETION='2', TEST_ITEM=value)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
