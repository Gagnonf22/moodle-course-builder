import io, json, subprocess, sys, tarfile, tempfile, unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'inspecter_mbz.py'

def archive(path, entries):
    with tarfile.open(path,'w') as t:
        for name,content,kind in entries:
            info=tarfile.TarInfo(name)
            if kind=='sym': info.type=tarfile.SYMTYPE;info.linkname='/etc/passwd';t.addfile(info)
            elif kind=='hard':info.type=tarfile.LNKTYPE;info.linkname='/etc/passwd';t.addfile(info)
            else:
                raw=content.encode();info.size=len(raw);t.addfile(info,io.BytesIO(raw))

class InspectorTests(unittest.TestCase):
    def run_case(self, entries=None, raw=None):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'test.mbz'
            if raw is not None:f.write_bytes(raw)
            else:archive(f,entries)
            return subprocess.run([sys.executable,str(SCRIPT),str(f)],text=True,capture_output=True)
    def test_module_count_and_course_format(self):
        r=self.run_case([('course/course.xml','<course><format>topics</format></course>','file'),('activities/page_1/module.xml','<module/>','file'),('activities/url_2/module.xml','<module/>','file')]);self.assertEqual(r.returncode,0,r.stderr);j=json.loads(r.stdout);self.assertEqual(j['module_count'],2);self.assertEqual(j['module_types'],{'page':1,'url':1});self.assertEqual(j['course_format'],'topics')
    def test_not_tar(self):
        r=self.run_case(raw=b'fake backup');self.assertNotEqual(r.returncode,0);self.assertIn('format TAR attendu',r.stderr)
    def test_traversal(self):
        r=self.run_case([('../outside','x','file')]);self.assertNotEqual(r.returncode,0);self.assertIn('non sûr',r.stderr)
    def test_absolute(self):
        r=self.run_case([('/etc/passwd','x','file')]);self.assertNotEqual(r.returncode,0)
    def test_symlink(self):
        r=self.run_case([('activities/link','', 'sym')]);self.assertNotEqual(r.returncode,0)
    def test_hardlink(self):
        r=self.run_case([('activities/link','', 'hard')]);self.assertNotEqual(r.returncode,0)
    def test_course_xml_over_limit(self):
        r=self.run_case([('course/course.xml','a'*(2*1024*1024+1),'file')]);self.assertNotEqual(r.returncode,0);self.assertIn('trop volumineuses',r.stderr)
    def test_dot_prefix_normalized_and_aliases_refused(self):
        r=self.run_case([('./course/course.xml','<course><format>topics</format></course>','file'),('./activities/page_1/module.xml','<module/>','file')])
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)['module_count'],1)
        self.assertEqual(json.loads(r.stdout)['course_format'],'topics')
        r=self.run_case([('./course/course.xml','<course/>','file'),('course/course.xml','<course/>','file')])
        self.assertNotEqual(r.returncode,0)
        self.assertIn('ambigu',r.stderr)
if __name__=='__main__':unittest.main()
