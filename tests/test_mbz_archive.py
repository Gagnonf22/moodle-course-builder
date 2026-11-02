"""Contrôles synthétiques ; ne prouvent pas une restauration dans Moodle."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

SPEC = importlib.util.spec_from_file_location('mbz_archive', Path(__file__).resolve().parents[1] / 'scripts/mbz_archive.py')
mbz = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mbz)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mbzt-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, names):
        path = self.root / 'input.mbz'
        with tarfile.open(path, 'w:gz') as archive:
            for name, kind in names:
                info = tarfile.TarInfo(name)
                if kind == 'link':
                    info.type, info.linkname = tarfile.SYMTYPE, '../outside'
                    archive.addfile(info)
                else:
                    info.size = 4
                    archive.addfile(info, io.BytesIO(b'test'))
        return path

    def test_windows_staging_permission_retry_is_bounded_and_does_not_overwrite(self):
        error = PermissionError('Windows refusal')
        error.winerror = 5
        target = self.root / 'target'
        with patch.object(Path, 'rename', side_effect=[error, None]) as rename, patch.object(mbz.time, 'sleep'):
            mbz._publier_dossier(self.root / 'stage', target)
            self.assertEqual(rename.call_count, 2)
        with patch.object(Path, 'rename', side_effect=error) as rename, patch.object(mbz.time, 'sleep'):
            with self.assertRaises(PermissionError):
                mbz._publier_dossier(self.root / 'stage', target)
            self.assertEqual(rename.call_count, 6)
        target.mkdir()
        with patch.object(Path, 'rename', side_effect=error) as rename, patch.object(mbz.time, 'sleep'):
            with self.assertRaises(FileExistsError):
                mbz._publier_dossier(self.root / 'stage', target)
            self.assertEqual(rename.call_count, 0)
        with patch.object(Path, 'rename', side_effect=PermissionError('not Windows')) as rename:
            with self.assertRaises(PermissionError):
                mbz._publier_dossier(self.root / 'stage', self.root / 'other')
            self.assertEqual(rename.call_count, 1)

    def test_roundtrip_index_ustar_and_unchanged_source(self):
        source = self.root / 'src'
        (source / 'course').mkdir(parents=True)
        xml = b'<course><name>Essai</name></course>'
        (source / 'course/course.xml').write_bytes(xml)
        (source / '.ARCHIVE_INDEX').write_bytes(b'ancien index')
        output = self.root / 'new.mbz'
        mbz.reemballer(source, output)
        self.assertEqual((source / '.ARCHIVE_INDEX').read_bytes(), b'ancien index')
        with tarfile.open(output) as archive:
            members = archive.getmembers()
            self.assertEqual(members[0].name, '.ARCHIVE_INDEX')
            self.assertTrue(all(not m.pax_headers for m in members))
            index = archive.extractfile(members[0]).read().decode().splitlines()
            self.assertEqual(index[0], f'Moodle archive file index. Count: {len(members)-1}')
            self.assertEqual(len(index)-1, len(members)-1)
            self.assertEqual(archive.extractfile('course/course.xml').read(), xml)
        dest = self.root / 'dest'
        dest.mkdir()
        mbz.extraire(output, dest)
        self.assertEqual((dest / 'course/course.xml').read_bytes(), xml)

    def test_unsafe_members_leave_destination_empty(self):
        for entries in [ [('good', 'file'), ('../outside', 'file')],
                         [('/absolute', 'file')], [('C:/drive', 'file')],
                         [('back\\slash', 'file')], [('link', 'link')],
                         [('same', 'file'), ('SAME', 'file')], [('nul', 'file')]]:
            with self.subTest(entries=entries):
                path = self.archive(entries)
                dest = self.root / 'out'
                with self.assertRaises(ValueError):
                    mbz.extraire(path, dest)
                self.assertFalse(dest.exists())
                self.assertFalse((self.root / 'outside').exists())

    def test_extraction_limits_and_nonempty_destination(self):
        path = self.archive([('a', 'file'), ('b', 'file')])
        for kwargs in ({'max_entries': 1}, {'max_bytes': 7}):
            with self.assertRaises(ValueError):
                mbz.extraire(path, self.root / 'dest', **kwargs)
        dest = self.root / 'dest'
        dest.mkdir()
        (dest / 'keep').write_bytes(b'original')
        with self.assertRaises(ValueError):
            mbz.extraire(path, dest)
        self.assertEqual((dest / 'keep').read_bytes(), b'original')

    def test_invalid_xml_and_ustar_failure_leave_no_output(self):
        source = self.root / 'src'
        source.mkdir()
        xml = source / 'course.xml'
        xml.write_bytes(b'<broken>')
        output = self.root / 'new.mbz'
        with self.assertRaises(Exception):
            mbz.reemballer(source, output)
        self.assertFalse(output.exists())
        self.assertEqual(xml.read_bytes(), b'<broken>')
        xml.write_bytes(b'<course/>')
        (source / ('x'*110)).write_bytes(b'long name')
        with self.assertRaises(ValueError):
            mbz.reemballer(source, output)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob('.mbz-*')), [])

    def test_existing_output_and_nested_output_refused(self):
        source = self.root / 'src'
        source.mkdir()
        output = self.root / 'keep.mbz'
        output.write_bytes(b'original')
        with self.assertRaises(FileExistsError):
            mbz.reemballer(source, output)
        self.assertEqual(output.read_bytes(), b'original')
        with self.assertRaises(ValueError):
            mbz.reemballer(source, source / 'nested.mbz')

    def test_publish_failure_leaves_source_and_output_untouched(self):
        from unittest.mock import patch
        source = self.root / 'src'
        source.mkdir()
        (source / 'course.xml').write_bytes(b'<course/>')
        output = self.root / 'new.mbz'
        with patch('fichiers.os.replace', side_effect=OSError('simulated failure')):
            with self.assertRaises(OSError):
                mbz.reemballer(source, output)
        self.assertFalse(output.exists())
        self.assertEqual((source / 'course.xml').read_bytes(), b'<course/>')
        self.assertEqual(list(self.root.glob('.mbz-*')), [])

    def test_exact_replacement_rejects_missing_and_ambiguous(self):
        path = self.root / 'replace.xml'
        path.write_bytes(b'<v>old old</v>')
        for motif in ('old', 'absent', ''):
            with self.assertRaises(ValueError):
                mbz.remplacer(path, motif, 'new')
            self.assertEqual(path.read_bytes(), b'<v>old old</v>')
        mbz.remplacer(path, 'old', 'new', compte=2)
        self.assertEqual(path.read_bytes(), b'<v>new new</v>')

    def test_replacement_preserves_crlf_lf_and_utf8_bom(self):
        path = self.root / 'mixed.xml'
        original = b'\xef\xbb\xbf<a>\r\n<b>X</b>\n</a>\r\n'
        path.write_bytes(original)
        mbz.remplacer(path, 'X', 'Y')
        self.assertEqual(path.read_bytes(), original.replace(b'X', b'Y'))


if __name__ == '__main__':
    unittest.main()
