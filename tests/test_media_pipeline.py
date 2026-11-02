"""Cas synthétiques de la chaîne média ; aucune donnée de cours intégrée."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import construire_h5p as build
import encoder_videos as encode
import nettoyer_vtt as captions
from fichiers import ecrire_nouveau, publier_nouveau, chemin_projet


def reference(questionnaire=False):
    libs = ['H5P.MultiChoice', 'H5P.TrueFalse', 'H5P.DragText',
            'H5P.QuestionSet' if questionnaire else 'H5P.InteractiveVideo']
    manifest = {'title': 'Synthetic', 'mainLibrary': libs[-1],
                'preloadedDependencies': [{'machineName': n, 'majorVersion': 1, 'minorVersion': 0} for n in libs]}
    actions = [{'action': {'library': n + ' 1.0', 'params': {'behaviour': {}}, 'subContentId': 'old'},
                'duration': {'from': 0, 'to': 1}} for n in libs[:3]]
    content = ({'introPage': {}, 'endGame': {}, 'questions': []} if questionnaire else
               {'interactiveVideo': {'assets': {'interactions': actions}, 'summary': {}}, 'override': {}, 'l10n': {}})
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as z:
        z.writestr('h5p.json', json.dumps(manifest))
        z.writestr('content/content.json', json.dumps(content))
        for lib in libs:
            z.writestr(lib + '-1.0/library.json', json.dumps({'machineName': lib, 'majorVersion': 1, 'minorVersion': 0}))
    return zipfile.ZipFile(io.BytesIO(stream.getvalue()))


QUESTION = {'type': 'MultiChoice', 'titre': 'Synthetic question', 'question': 'Choose',
            'reponses': [{'texte': 'A', 'correct': True, 'retro': 'Yes'}, {'texte': 'B', 'correct': False, 'retro': 'No'}]}


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mcbt-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_new_output_and_failed_publish_preserve_existing_data(self):
        dst = self.root / 'out'
        ecrire_nouveau(dst, b'first')
        with self.assertRaises(FileExistsError):
            ecrire_nouveau(dst, b'second')
        self.assertEqual(dst.read_bytes(), b'first')
        temp = self.root / 'temp'
        temp.write_bytes(b'ready')
        other = self.root / 'other'
        with patch('fichiers.os.replace', side_effect=OSError('failed')):
            with self.assertRaises(OSError):
                publier_nouveau(temp, other)
        self.assertFalse(other.exists())
        self.assertEqual(temp.read_bytes(), b'ready')

    def test_relative_media_cannot_escape_project(self):
        sub = self.root / 'sub'
        sub.mkdir()
        (self.root / 'private').write_bytes(b'outside')
        with self.assertRaises(ValueError):
            chemin_projet(sub, '../private')
        with self.assertRaises(ValueError):
            chemin_projet(sub, self.root / 'private')

    def test_caption_corrections_wrapping_settings_and_crlf_input(self):
        src, dst = self.root / 'in.vtt', self.root / 'out.vtt'
        src.write_bytes(b'WEBVTT\r\n\r\ncue-id\r\n00:00.000 --> 00:04.000 align:start\r\nAlpha beta gamma delta epsilon zeta\r\n')
        corrections = self.root / 'corrections.json'
        corrections.write_text('[["Alpha", "Omega"]]', encoding='utf-8')
        stats = captions.nettoyer(src, dst, corrections=captions.charger_corrections(corrections), largeur=12, nombre_lignes=1)
        text = dst.read_text(encoding='utf-8')
        self.assertGreater(stats['repliques'], 1)
        self.assertIn('Omega', text)
        self.assertNotIn('Alpha', text)
        self.assertNotIn(b'\r', dst.read_bytes())
        self.assertIn('00:00:04.000 align:start', text)
        self.assertEqual(src.read_bytes().count(b'\r\n'), 5)

    def test_caption_thanks_not_removed_without_option(self):
        src = self.root / 'in.vtt'
        src.write_text('WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nMerci!\n\n00:00:01.000 --> 00:00:02.000\nAnother cue\n', encoding='utf-8')
        kept = self.root / 'kept.vtt'
        removed = self.root / 'removed.vtt'
        self.assertEqual(captions.nettoyer(src, kept)['supprimees'], 0)
        self.assertEqual(captions.nettoyer(src, removed, retirer_hallucinations=True)['supprimees'], 1)
        self.assertIn('Merci!', kept.read_text())
        self.assertNotIn('Merci!', removed.read_text())

    def test_caption_malformed_or_empty_result_not_published(self):
        src, dst = self.root / 'in.vtt', self.root / 'out.vtt'
        for text in ('bad header', 'WEBVTT\n\n00:00:02.000 --> 00:00:01.000\nText',
                     'WEBVTT\n\nSTYLE\n::cue { color: red; }'):
            src.write_text(text)
            with self.assertRaises(ValueError):
                captions.nettoyer(src, dst)
            self.assertFalse(dst.exists())

    def test_timestamp_rounding_does_not_produce_sixty_seconds(self):
        self.assertEqual(captions.horodatage(59.9999), '00:01:00.000')

    def test_note_like_identifier_is_a_cue_not_a_comment(self):
        src, dst = self.root / 'in.vtt', self.root / 'out.vtt'
        src.write_text('WEBVTT\n\nNOTE123\n00:00:00.000 --> 00:00:01.000\nKeep this cue\n', encoding='utf-8')
        self.assertEqual(captions.nettoyer(src, dst)['repliques'], 1)
        self.assertIn('Keep this cue', dst.read_text())

    def test_invalid_numeric_thresholds_and_output_identifiers_rejected(self):
        base = {'type': 'QuestionSet', 'identifiant': 'test', 'titre': 'Test', 'titre_activite': 'Activity',
                'introduction': '', 'seuil': 50, 'retro_globale': [], 'questions': [copy.deepcopy(QUESTION)]}
        for value in (float('nan'), float('inf'), True, -1, 101):
            spec = dict(base, seuil=value)
            with self.assertRaises(ValueError):
                build.valider_fiche(spec)
        with self.assertRaises(ValueError):
            build.valider_fiche(dict(base, identifiant='../outside'))

    def test_verifier_rejects_media_outside_content_and_wrong_library_version(self):
        (self.root / 'content').mkdir()
        (self.root / 'private').write_bytes(b'outside')
        lib = self.root / 'H5P.MultiChoice-1.0'
        lib.mkdir()
        (lib / 'library.json').write_text('{"machineName":"H5P.MultiChoice","majorVersion":2,"minorVersion":0}')
        manifest = {'preloadedDependencies':[{'machineName':'H5P.MultiChoice','majorVersion':1,'minorVersion':0}]}
        errors = build.verifier(self.root, manifest, {'path':'../private','library':'H5P.MultiChoice 1.0'})
        self.assertTrue(any('hors contenu' in e for e in errors))
        self.assertTrue(any('incohérent' in e for e in errors))

    def test_question_set_from_configuration_and_no_overwrite(self):
        refs = {'video': reference(), 'questionnaire': reference(True)}
        self.addCleanup(lambda: [z.close() for z in refs.values()])
        fiche = {'type': 'QuestionSet', 'identifiant': 'synthetic', 'titre': 'Test', 'titre_activite': 'Activity',
                 'introduction': 'Intro', 'seuil': 60, 'retro_globale': [[0, 59, 'Retry'], [60, 100, 'Done']],
                 'questions': [copy.deepcopy(QUESTION)]}
        path = self.root / 'spec.json'
        path.write_text(json.dumps(fiche))
        args = SimpleNamespace(projet=self.root, sortie=self.root / 'out', ffmpeg=None, affiches=None, limite_mio=None)
        dst = build.construire(path, args, refs)
        initial = dst.read_bytes()
        with zipfile.ZipFile(dst) as z:
            content = json.loads(z.read('content/content.json'))
            self.assertEqual(content['passPercentage'], 60)
            self.assertFalse(content['questions'][0]['params']['behaviour']['enableRetry'])
            self.assertEqual(json.loads(z.read('h5p.json'))['title'], 'Activity')
        with self.assertRaises(FileExistsError):
            build.construire(path, args, refs)
        self.assertEqual(dst.read_bytes(), initial)

    def test_manifest_limit_and_unsupported_types_do_not_publish(self):
        refs = {'video': reference(), 'questionnaire': reference(True)}
        self.addCleanup(lambda: [z.close() for z in refs.values()])
        fiche = {'type': 'QuestionSet', 'identifiant': 'tiny', 'titre': 'Test', 'titre_activite': 'Activity',
                 'introduction': '', 'seuil': 50, 'retro_globale': [], 'questions': [copy.deepcopy(QUESTION)]}
        path = self.root / 'spec.json'
        path.write_text(json.dumps(fiche))
        args = SimpleNamespace(projet=self.root, sortie=self.root / 'out', ffmpeg=None, affiches=None, limite_mio=0.00001)
        with self.assertRaises(ValueError):
            build.construire(path, args, refs)
        self.assertFalse((args.sortie / 'tiny.h5p').exists())
        fiche['questions'][0]['type'] = 'unknown'
        with self.assertRaises(ValueError):
            build.valider_fiche(fiche)

    def test_reference_selection_normalizes_dot_prefix_and_rejects_ambiguity(self):
        with reference() as z:
            blob = io.BytesIO()
            with zipfile.ZipFile(blob, 'w') as output:
                for name in z.namelist():
                    output.writestr(name, z.read(name))
        raw = blob.getvalue()
        sha = hashlib.sha1(raw).hexdigest()
        metadata = f'<files><file><filename>video-example.h5p</filename><contenthash>{sha}</contenthash></file><file><filename>video-other.h5p</filename><contenthash>{"a"*40}</contenthash></file></files>'.encode()
        archive = self.root / 'reference.mbz'
        with tarfile.open(archive, 'w:gz') as tar:
            for name, data in [('./files.xml', metadata), (f'./files/{sha[:2]}/{sha}', raw)]:
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        with build.paquet_reference(archive, 'video-example') as selected:
            self.assertIn('h5p.json', selected.namelist())
        with self.assertRaises(ValueError):
            build.paquet_reference(archive, 'video-')
        with self.assertRaises(ValueError):
            build.paquet_reference(archive, 'absent')

    def test_reference_zip_path_escape_refused(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as z:
            z.writestr('../outside', 'bad')
        with zipfile.ZipFile(io.BytesIO(stream.getvalue())) as z:
            with self.assertRaises(ValueError):
                build.extraire_bibliotheques(z, self.root / 'libs')
        self.assertFalse((self.root.parent / 'outside').exists())

    def test_encoder_refuses_source_destination_and_failed_transcode(self):
        src = self.root / 'source.mp4'
        src.write_bytes(b'original')
        with self.assertRaises(FileExistsError):
            encode.encoder(src, src)
        dst = self.root / 'out.mp4'
        with patch.object(encode, 'trouver_ffmpeg', return_value='synthetic'), \
             patch.object(encode.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'synthetic')):
            with self.assertRaises(subprocess.CalledProcessError):
                encode.encoder(src, dst)
        self.assertEqual(src.read_bytes(), b'original')
        self.assertFalse(dst.exists())
        self.assertEqual(list(self.root.glob('.mcb-*')), [])


@unittest.skipUnless(os.environ.get('FFMPEG_EXE'), 'FFMPEG_EXE absent : encodage réel non testé')
class FfmpegTests(unittest.TestCase):
    def test_synthetic_video_codec_resolution_fps_and_mono(self):
        ff = encode.trouver_ffmpeg()
        with tempfile.TemporaryDirectory(prefix='mcbf-') as tmp:
            src, dst = Path(tmp) / 'source.avi', Path(tmp) / 'result.mp4'
            subprocess.run([ff, '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=2048x1152:rate=30',
                            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=44100', '-t', '1',
                            '-c:v', 'mpeg4', '-q:v', '10', '-c:a', 'pcm_s16le', '-ac', '2', str(src)], check=True)
            original = hashlib.sha256(src.read_bytes()).hexdigest()
            encode.encoder(src, dst, preset='ultrafast')
            decoded = subprocess.run([ff, '-hide_banner', '-i', str(dst), '-f', 'null', '-'], capture_output=True, text=True, check=True)
            self.assertIn('Video: h264', decoded.stderr)
            self.assertIn('1920x1080', decoded.stderr)
            self.assertIn('15 fps', decoded.stderr)
            self.assertRegex(decoded.stderr, r'Audio: aac[^\n]*mono')
            self.assertRegex(decoded.stderr, r'Duration: 00:00:01\.[0-2]\d')
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(), original)

    def test_silent_small_video_is_not_upscaled(self):
        ff = encode.trouver_ffmpeg()
        with tempfile.TemporaryDirectory(prefix='mcbf-') as tmp:
            src, dst = Path(tmp) / 'silent.mp4', Path(tmp) / 'result.mp4'
            subprocess.run([ff, '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=size=320x240:rate=15',
                            '-t', '0.5', '-c:v', 'libx264', str(src)], check=True)
            encode.encoder(src, dst, preset='ultrafast')
            decoded = subprocess.run([ff, '-hide_banner', '-i', str(dst), '-f', 'null', '-'], capture_output=True, text=True, check=True)
            self.assertIn('320x240', decoded.stderr)


if __name__ == '__main__':
    unittest.main()
