"""Paquets synthétiques : stabilité, évolution et langue ; aucune donnée Moodle."""
from contextlib import redirect_stderr, ExitStack
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
import uuid
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import construire_h5p as build
from test_media_pipeline import reference, QUESTION


class StableH5pTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mcb3a-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.refs = {'video': self.stack.enter_context(reference()),
                     'questionnaire': self.stack.enter_context(reference(True))}
        (self.root / 'video.mp4').write_bytes(b'fake-video-no-decoding-in-this-test')
        (self.root / 'captions.vtt').write_bytes(b'WEBVTT\n\n00:00.000 --> 00:01.000\nExample\n')
        posters = self.root / 'posters'
        posters.mkdir()
        (posters / 'synthetic-affiche.jpg').write_bytes(b'fake-poster-no-decoding')
        self.args = SimpleNamespace(projet=self.root, sortie=self.root / 'out', ffmpeg=None,
                                    affiches=posters, limite_mio=None)
        self.counter = 0

    def video(self):
        return dict(type='InteractiveVideo', identifiant='synthetic', titre='Example', titre_activite='Activity',
                    video='video.mp4', sous_titres='captions.vtt', fin=60,
                    interactions=[dict(copy.deepcopy(QUESTION), cle='first', temps=10),
                                  dict(copy.deepcopy(QUESTION), cle='last', temps=40)])

    def quiz(self):
        return dict(type='QuestionSet', identifiant='synthetic', titre='Example', titre_activite='Activity',
                    introduction='', seuil=50, retro_globale=[],
                    questions=[dict(copy.deepcopy(QUESTION), cle='first'), dict(copy.deepcopy(QUESTION), cle='last')])

    def package(self, spec, **options):
        self.counter += 1
        args = copy.copy(self.args)
        args.sortie = self.root / f'out{self.counter}'
        for k, v in options.items():
            setattr(args, k, v)
        path = self.root / f'spec{self.counter}.json'
        path.write_text(json.dumps(spec), encoding='utf-8')
        messages = io.StringIO()
        with redirect_stderr(messages):
            dst = build.construire(path, args, self.refs)
        with zipfile.ZipFile(dst) as z:
            raw = z.read('content/content.json')
            return raw, json.loads(raw), z.namelist(), messages.getvalue()

    def ids(self, content, kind):
        return ([q['subContentId'] for q in content['questions']] if kind == 'QuestionSet' else
                [q['action']['subContentId'] for q in content['interactiveVideo']['assets']['interactions']])

    def test_repeated_video_and_question_set_content_are_byte_identical(self):
        for spec in (self.video(), self.quiz()):
            a = self.package(spec)
            b = self.package(spec)
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[3], '')
            self.assertTrue(all(uuid.UUID(x).version == 5 for x in self.ids(a[1], spec['type'])))

    def test_insertion_reordering_and_text_edit_preserve_existing_ids(self):
        for spec in (self.video(), self.quiz()):
            kind = spec['type']
            field = 'questions' if kind == 'QuestionSet' else 'interactions'
            original = self.ids(self.package(spec)[1], kind)
            inserted = dict(copy.deepcopy(QUESTION), cle='inserted')
            if kind == 'InteractiveVideo':
                inserted['temps'] = 25
            spec[field].insert(1, inserted)
            fresh = self.ids(self.package(spec)[1], kind)
            self.assertEqual([fresh[0], fresh[2]], original)
            self.assertEqual(len(set(fresh)), 3)
            spec[field][0]['question'] = 'Reworded'
            spec[field].reverse()
            if kind == 'InteractiveVideo':
                for q, t in zip(spec[field], [10, 25, 40]):
                    q['temps'] = t
            self.assertEqual(self.ids(self.package(spec)[1], kind), fresh[::-1])

    def test_duplicate_and_invalid_keys_refused_before_output(self):
        for spec in (self.video(), self.quiz()):
            field = 'questions' if spec['type'] == 'QuestionSet' else 'interactions'
            for key in ('first', '', None, 123, 'with space'):
                changed = copy.deepcopy(spec)
                changed[field][1]['cle'] = key
                with self.assertRaises(ValueError):
                    self.package(changed)
        self.assertEqual(list(self.root.glob('out*')), [])

    def test_missing_keys_warn_and_keep_legacy_random_ids(self):
        spec = self.video()
        del spec['interactions'][0]['cle']
        first, second = self.package(spec), self.package(spec)
        a, b = self.ids(first[1], spec['type']), self.ids(second[1], spec['type'])
        self.assertNotEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])
        self.assertIn('1 interaction(s) sans cle', first[3])
        self.assertEqual(uuid.UUID(a[0]).version, 4)

    def test_new_fiche_identifier_or_new_key_changes_uuid(self):
        first = build.identifiant_interaction({'cle': 'one'}, 'package-a')
        self.assertNotEqual(first, build.identifiant_interaction({'cle': 'one'}, 'package-b'))
        self.assertNotEqual(first, build.identifiant_interaction({'cle': 'two'}, 'package-a'))

    def test_legacy_french_track_and_custom_english_track(self):
        legacy = self.package(self.video())
        track = legacy[1]['interactiveVideo']['video']['textTracks']
        self.assertEqual(track['defaultTrackLabel'], 'Français')
        self.assertEqual(track['videoTrack'][0]['srcLang'], 'fr')
        self.assertIn('content/files/synthetic.fr.vtt', legacy[2])
        spec = dict(self.video(), langue_sous_titres='en-GB', libelle_sous_titres='English')
        english = self.package(spec)
        tracks = english[1]['interactiveVideo']['video']['textTracks']
        self.assertEqual(tracks['defaultTrackLabel'], 'English')
        self.assertEqual(tracks['videoTrack'][0]['srcLang'], 'en-GB')
        self.assertEqual(tracks['videoTrack'][0]['track']['path'], 'files/synthetic.en-GB.vtt')
        self.assertIn('content/files/synthetic.en-GB.vtt', english[2])

    def test_cli_language_fallback_and_fiche_precedence(self):
        result = self.package(self.video(), langue_sous_titres='en', libelle_sous_titres='English')
        track = result[1]['interactiveVideo']['video']['textTracks']['videoTrack'][0]
        self.assertEqual((track['srcLang'], track['label']), ('en', 'English'))
        spec = dict(self.video(), langue_sous_titres='fr-CA', libelle_sous_titres='Français canadien')
        result = self.package(spec, langue_sous_titres='en', libelle_sous_titres='English')
        track = result[1]['interactiveVideo']['video']['textTracks']['videoTrack'][0]
        self.assertEqual((track['srcLang'], track['label']), ('fr-CA', 'Français canadien'))

    def test_invalid_language_and_labels_refused_before_output(self):
        for value in ('', '../en', 'english', 'en_US', 'en/GB', 123, None):
            with self.assertRaises(ValueError):
                self.package(dict(self.video(), langue_sous_titres=value))
        for value in ('', '   ', 'English\n', 'English\x7f', 'English\x85', 123):
            with self.assertRaises(ValueError):
                self.package(dict(self.video(), libelle_sous_titres=value))
        self.assertEqual(list(self.root.glob('out*')), [])

    def test_cli_rejects_invalid_language_before_opening_reference(self):
        result = subprocess.run([sys.executable, str(Path(build.__file__)), 'missing.json', '--mbz', 'missing.mbz',
                                 '--reference-video', 'video', '--projet', '.', '--sortie', str(self.root / 'out'),
                                 '--langue-sous-titres', '../en'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Code de langue', result.stderr)
        self.assertNotIn('FileNotFoundError', result.stderr)


if __name__ == '__main__':
    unittest.main()
