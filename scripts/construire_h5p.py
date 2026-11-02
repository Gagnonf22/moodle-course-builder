"""Construire Interactive Video / Question Set depuis des fiches et références explicites.

Les versions des bibliothèques viennent des paquets de référence sélectionnés,
pas d'une hypothèse sur l'installation cible. Aucun appel à Moodle.
"""
import argparse, copy, html, io, json, os, re, shutil, stat, subprocess, sys, tarfile, tempfile, uuid, zipfile
from pathlib import Path, PurePosixPath
from contextlib import ExitStack
import xml.etree.ElementTree as ET
import math
import hashlib
import unicodedata

from encoder_videos import trouver_ffmpeg
from fichiers import chemin_projet, publier_nouveau
TITRES_LIB = {"MultiChoice": "Multiple Choice", "TrueFalse": "True/False Question", "DragText": "Drag the Words"}
TYPES_LIB = {"MultiChoice": "Choix multiples", "TrueFalse": "Vrai ou faux", "DragText": "Glisser les mots"}
ESPACE_INTERACTIONS = uuid.uuid5(uuid.NAMESPACE_URL, 'urn:moodle-course-builder:h5p:interaction:v1')


def langue_sous_titres(fiche, langue_defaut='fr', libelle_defaut=None):
    """Sous-ensemble explicite de codes BCP 47 usuels, sans libellé inventé."""
    code = fiche.get('langue_sous_titres', langue_defaut)
    if not isinstance(code, str) or not re.fullmatch(r'[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', code):
        raise ValueError('Code de langue de sous-titres invalide (exemples : fr, en, fr-CA)')
    libelle = fiche.get('libelle_sous_titres', libelle_defaut)
    if libelle is None:
        libelle = 'Français' if code.lower() == 'fr' else code
    if not isinstance(libelle, str) or not libelle.strip() or any(unicodedata.category(c) == 'Cc' for c in libelle):
        raise ValueError('Libellé de sous-titres non vide attendu')
    return code, libelle


def identifiant_interaction(spec, identifiant_fiche):
    if 'cle' not in spec:
        return str(uuid.uuid4())
    if not identifiant_fiche:
        raise ValueError('Identifiant de fiche requis pour une interaction à clé')
    nom = json.dumps([identifiant_fiche, spec['cle']], ensure_ascii=False, separators=(',', ':'))
    return str(uuid.uuid5(ESPACE_INTERACTIONS, nom))


def paquet_reference(mbz, motif):
    """Sélection non ambiguë par motif de nom ; pas d'extraction du gros .mbz."""
    if not isinstance(motif, str) or not motif:
        raise ValueError('Un motif de référence non vide est requis')
    matches = set()
    with tarfile.open(mbz, 'r|gz') as tar:
        for member in tar:
            if member.name.removeprefix('./') != 'files.xml':
                continue
            if not member.isfile() or member.size > 32 * 1024**2:
                raise ValueError('Métadonnées files.xml absentes ou trop grandes')
            root = ET.fromstring(tar.extractfile(member).read())
            for row in root.findall('file'):
                name = row.findtext('filename') or ''
                if name.lower().endswith('.h5p') and motif.casefold() in name.casefold():
                    matches.add(row.findtext('contenthash'))
            break
    if len(matches) != 1:
        raise ValueError(f'Référence absente ou ambiguë pour le motif {motif!r} : {len(matches)} contenus')
    contenthash = matches.pop()
    if not contenthash or not re.fullmatch('[0-9a-f]{40}', contenthash):
        raise ValueError('Empreinte de référence invalide')
    with tarfile.open(mbz, 'r|gz') as tar:
        for member in tar:
            name = member.name.removeprefix('./')
            if name.startswith('files/') and name.rsplit('/',1)[-1] == contenthash:
                if not member.isfile() or member.size > 512 * 1024**2:
                    raise ValueError('Paquet de référence trop grand ou non régulier')
                raw = tar.extractfile(member).read()
                if hashlib.sha1(raw).hexdigest() != contenthash:
                    raise ValueError('Empreinte du paquet de référence incohérente')
                return zipfile.ZipFile(io.BytesIO(raw))
    raise ValueError('La référence est déclarée mais son paquet n’est pas intégré à cette sauvegarde')


def valider_fiche(fiche):
    if not isinstance(fiche, dict):
        raise ValueError('La fiche doit être un objet JSON')
    def nombre(value):
        return type(value) in (int, float) and math.isfinite(value)
    for key in ('identifiant', 'titre', 'titre_activite'):
        if not isinstance(fiche.get(key), str) or not fiche[key]:
            raise ValueError(f'Champ requis : {key}')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', fiche['identifiant']):
        raise ValueError('Identifiant de fichier invalide')
    kind = fiche.get('type', 'InteractiveVideo')
    if kind not in {'QuestionSet', 'InteractiveVideo'}:
        raise ValueError('Seuls InteractiveVideo et QuestionSet sont constructibles par ce script')
    questions = fiche.get('questions' if kind == 'QuestionSet' else 'interactions')
    if not isinstance(questions, list) or not questions:
        raise ValueError('Au moins une question est requise')
    cles = set()
    for q in questions:
        if not isinstance(q, dict):
            raise ValueError('Chaque question doit être un objet JSON')
        if 'cle' in q:
            cle = q['cle']
            if not isinstance(cle, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', cle):
                raise ValueError('Clé d’interaction invalide : lettres, chiffres, tirets ou underscores attendus')
            if cle in cles:
                raise ValueError('Clé d’interaction dupliquée dans la fiche')
            cles.add(cle)
        if q.get('type') not in TYPES_LIB or not isinstance(q.get('titre'), str):
            raise ValueError('Type de question ou titre invalide')
        if q['type'] == 'MultiChoice':
            answers = q.get('reponses', [])
            if (not isinstance(answers, list) or any(not isinstance(a, dict) for a in answers)
                    or len(answers) < 2 or not any(a.get('correct') is True for a in answers)):
                raise ValueError('Choix multiples : deux options et une réponse correcte au minimum')
            if any(type(a.get('correct')) is not bool or not isinstance(a.get('texte'), str)
                   or not isinstance(a.get('retro'), str) for a in answers):
                raise ValueError('Réponse ou rétroaction mal formée')
        elif q['type'] == 'TrueFalse':
            if type(q.get('correct')) is not bool:
                raise ValueError('Vrai/faux : correct doit être booléen')
            for key in ('retro_bonne', 'retro_mauvaise'):
                if not isinstance(q.get(key), str):
                    raise ValueError('Rétroaction vrai/faux requise')
        elif not isinstance(q.get('texte'), str) or q['texte'].count('*') < 2:
            raise ValueError('Glisser les mots : texte à trous requis')
        key = 'consigne' if q['type'] == 'DragText' else 'question'
        if not isinstance(q.get(key), str):
            raise ValueError(f'Champ de question requis : {key}')
    if kind == 'QuestionSet':
        if not nombre(fiche.get('seuil')) or not 0 <= fiche['seuil'] <= 100:
            raise ValueError('Seuil attendu entre 0 et 100')
        if not isinstance(fiche.get('introduction'), str) or not isinstance(fiche.get('retro_globale'), list):
            raise ValueError('Introduction et rétroactions globales requises')
        for feedback in fiche['retro_globale']:
            if (not isinstance(feedback, list) or len(feedback) != 3 or
                    not all(nombre(v) for v in feedback[:2]) or
                    not 0 <= feedback[0] <= feedback[1] <= 100 or not isinstance(feedback[2], str)):
                raise ValueError('Plage de rétroaction globale invalide')
    else:
        langue_sous_titres(fiche)
        end = fiche.get('fin')
        if not nombre(end) or end <= 0:
            raise ValueError('Fin de vidéo invalide')
        times = [q.get('temps') for q in questions]
        if any(not nombre(t) or t < 0 or t+0.5 > end for t in times) or times != sorted(set(times)):
            raise ValueError('Temps des interactions invalides, désordonnés ou dupliqués')
        for key in ('video','sous_titres'):
            if not isinstance(fiche.get(key), str):
                raise ValueError(f'Média requis : {key}')
        if not nombre(fiche.get('affiche_temps', 0)) or not 0 <= fiche.get('affiche_temps', 0) < end:
            raise ValueError('Temps de l’affiche invalide')
        for bookmark in fiche.get('signets', []):
            if (not isinstance(bookmark, list) or len(bookmark) != 2 or not nombre(bookmark[0])
                    or not 0 <= bookmark[0] <= end or not isinstance(bookmark[1], str)):
                raise ValueError('Signet invalide')


def extraire_bibliotheques(reference, destination):
    """Copier seulement les bibliothèques ; refuser chemins et liens ambigus."""
    members = reference.infolist()
    if len(members) > 100000 or sum(m.file_size for m in members) > 2 * 1024**3:
        raise ValueError('Référence H5P trop grande')
    seen = set()
    for member in members:
        path = PurePosixPath(member.filename)
        key = '/'.join(path.parts).casefold()
        if (path.is_absolute() or '..' in path.parts or '\\' in member.filename
                or ':' in member.filename or key in seen
                or stat.S_ISLNK(member.external_attr >> 16)):
            raise ValueError('Entrée ZIP de référence refusée')
        seen.add(key)
        if member.is_dir() or member.filename == 'h5p.json' or path.parts[0] == 'content':
            continue
        if not re.fullmatch(r'[A-Za-z0-9_.-]+-\d+\.\d+', path.parts[0]):
            raise ValueError('Fichier hors bibliothèque dans la référence')
        target = Path(destination).joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(reference.read(member))


def para(texte):
    return f"<p>{html.escape(texte, quote=False)}</p>\n"


def gabarits(ref_content):
    """Premier exemple de chaque type de question dans le paquet de référence."""
    g = {}
    for it in ref_content["interactiveVideo"]["assets"]["interactions"]:
        cle = it["action"]["library"].split()[0].split(".")[1]
        g.setdefault(cle, it)
    return g


def question(spec, g, notee=False, identifiant_fiche=None):
    """Bloc `action` H5P (bibliothèque, paramètres, métadonnées) d'une question."""
    t = spec["type"]
    action = copy.deepcopy(g[t]["action"])
    p = action["params"]
    if t == "MultiChoice":
        p["question"] = para(spec["question"])
        p["answers"] = [{"text": f"<div>{html.escape(r['texte'], quote=False)}</div>\n", "correct": r["correct"],
                         "tipsAndFeedback": {"tip": "", "chosenFeedback": f"<div>{html.escape(r['retro'], quote=False)}</div>\n",
                                             "notChosenFeedback": ""}} for r in spec["reponses"]]
        p["behaviour"]["type"] = "single" if sum(r["correct"] for r in spec["reponses"]) == 1 else "multi"
    elif t == "TrueFalse":
        p["question"] = para(spec["question"])
        p["correct"] = "true" if spec["correct"] else "false"
        p["behaviour"]["feedbackOnCorrect"] = spec["retro_bonne"]
        p["behaviour"]["feedbackOnWrong"] = spec["retro_mauvaise"]
    elif t == "DragText":
        p["taskDescription"] = para(spec["consigne"])
        p["textField"] = spec["texte"]
        p["distractors"] = spec.get("distracteurs", "")
    else:
        sys.exit(f"Type non pris en charge : {t}")
    if notee:  # questionnaire final : une seule tentative par question, solution visible
        p["behaviour"]["enableRetry"] = False
    action["subContentId"] = identifiant_interaction(spec, identifiant_fiche)
    action["metadata"] = {"contentType": TYPES_LIB[t], "license": "U", "title": spec["titre"]}
    return action


def fenetre(fiche, n):
    """Fin d'affichage : 10 s au plus, sans chevaucher l'interaction suivante ni l'écran de fin."""
    debut = fiche["interactions"][n]["temps"]
    suivantes = [i["temps"] for i in fiche["interactions"][n + 1:]] + [fiche["fin"]]
    return max(debut + 0.5, min(debut + 10, min(suivantes) - 1))


def interaction(spec, g, fin_fenetre, identifiant_fiche=None):
    it = copy.deepcopy(g[spec["type"]])
    it["action"] = question(spec, g, identifiant_fiche=identifiant_fiche)
    it["duration"] = {"from": spec["temps"], "to": fin_fenetre}
    it["pause"] = True
    it["label"] = ""
    it["libraryTitle"] = TITRES_LIB[spec["type"]]
    return it


def contenu_video(fiche, ref_content, g, c, projet, ffmpeg, affiches=None):
    slug = fiche["identifiant"]
    langue, libelle = langue_sous_titres(fiche)
    video = chemin_projet(projet, fiche["video"])
    for sous in ("videos", "images", "files"):
        os.makedirs(os.path.join(c, sous))
    shutil.copyfile(video, os.path.join(c, "videos", f"{slug}.mp4"))
    shutil.copyfile(chemin_projet(projet, fiche["sous_titres"]), os.path.join(c, "files", f"{slug}.{langue}.vtt"))
    if affiches:
        shutil.copyfile(chemin_projet(affiches, f'{slug}-affiche.jpg'), os.path.join(c, 'images', f'{slug}-affiche.jpg'))
    else:
        subprocess.run([trouver_ffmpeg(ffmpeg), "-v", "error", "-y", "-ss", str(fiche.get("affiche_temps", 0)), "-i", str(video),
                    "-frames:v", "1", "-vf", "scale=1280:720", "-q:v", "4",
                    os.path.join(c, "images", f"{slug}-affiche.jpg")], check=True)
    return {
        "interactiveVideo": {
            "video": {
                "startScreenOptions": {"title": fiche["titre"], "hideStartTitle": False,
                                       "shortStartDescription": fiche.get("description", ""),
                                       "poster": {"path": f"images/{slug}-affiche.jpg", "mime": "image/jpeg",
                                                  "width": 1280, "height": 720, "copyright": {"license": "U"}}},
                "textTracks": {"videoTrack": [{"label": libelle, "kind": "subtitles", "srcLang": langue,
                                               "track": {"path": f"files/{slug}.{langue}.vtt", "mime": "text/vtt",
                                                         "copyright": {"license": "U"}}}],
                               "defaultTrackLabel": libelle},
                "files": [{"path": f"videos/{slug}.mp4", "mime": "video/mp4", "copyright": {"license": "U"}}],
            },
            "assets": {
                "interactions": [interaction(i, g, fenetre(fiche, n), fiche['identifiant']) for n, i in enumerate(fiche["interactions"])],
                "bookmarks": [{"time": t, "label": l} for t, l in fiche.get("signets", [])],
                "endscreens": [{"time": fiche["fin"], "label": fiche.get("fin_libelle", "Fin")}],
            },
            "summary": ref_content["interactiveVideo"]["summary"],
        },
        "override": ref_content["override"],
        "l10n": ref_content["l10n"],
    }


def contenu_questionnaire(fiche, ref_q, g):
    content = copy.deepcopy(ref_q)
    content["introPage"]["title"] = fiche["titre"]
    content["introPage"]["introduction"] = para(fiche["introduction"])
    content["passPercentage"] = fiche["seuil"]
    content["randomQuestions"] = False
    content["endGame"]["overallFeedback"] = [{"from": a, "to": b, "feedback": t} for a, b, t in fiche["retro_globale"]]
    content["questions"] = [question(q, g, notee=True, identifiant_fiche=fiche['identifiant']) for q in fiche["questions"]]
    return content


def verifier(dossier, h5p_json, content):
    """Contrôles structurels avant l'emballage."""
    erreurs = []
    libs = set(os.listdir(dossier))
    deps = {f"{d['machineName']}-{d['majorVersion']}.{d['minorVersion']}" for d in h5p_json["preloadedDependencies"]}
    erreurs += [f"Bibliothèque absente du paquet : {d}" for d in deps - libs]
    for dep in h5p_json['preloadedDependencies']:
        name = f"{dep['machineName']}-{dep['majorVersion']}.{dep['minorVersion']}"
        path = Path(dossier) / name / 'library.json'
        if not path.is_file():
            erreurs.append(f'Manifeste de bibliothèque absent : {name}')
            continue
        meta = json.loads(path.read_text(encoding='utf-8-sig'))
        if any(str(meta.get(k)) != str(dep[k]) for k in ('machineName','majorVersion','minorVersion')):
            erreurs.append(f'Manifeste de bibliothèque incohérent : {name}')
    content_root = (Path(dossier) / 'content').resolve()
    def walk(node):
        if isinstance(node, dict):
            library = node.get('library')
            if isinstance(library, str):
                match = re.fullmatch(r'([\w.]+) (\d+\.\d+)', library)
                if not match or f'{match[1]}-{match[2]}' not in deps:
                    erreurs.append(f'Dépendance non déclarée : {library}')
            chemin = node.get('path')
            if isinstance(chemin, str) and not re.match(r'^https?://', chemin):
                target = (content_root / chemin).resolve()
                if not target.is_relative_to(content_root) or not target.is_file():
                    erreurs.append(f'Fichier local absent ou hors contenu : {chemin}')
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
    walk(content)
    return erreurs


def construire(chemin_fiche, a, refs):
    fiche = json.loads(Path(chemin_fiche).read_text(encoding='utf-8-sig'))
    if fiche.get('type', 'InteractiveVideo') == 'InteractiveVideo':
        langue, libelle = langue_sous_titres(fiche, getattr(a, 'langue_sous_titres', 'fr'),
                                          getattr(a, 'libelle_sous_titres', None))
        fiche = dict(fiche, langue_sous_titres=langue, libelle_sous_titres=libelle)
    valider_fiche(fiche)
    questions = fiche.get('questions', fiche.get('interactions', []))
    sans_cle = sum('cle' not in q for q in questions)
    if sans_cle:
        print(f"AVERTISSEMENT : {sans_cle} interaction(s) sans cle ; UUID aléatoires, non reproductibles.", file=sys.stderr)
    projet = a.projet
    questionnaire = fiche.get("type") == "QuestionSet"
    ref = refs['questionnaire' if questionnaire else 'video']
    ref_content = json.loads(ref.read("content/content.json"))
    g = gabarits(json.loads(refs['video'].read("content/content.json")))
    required = {q['type'] for q in fiche.get('questions', fiche.get('interactions',[]))}
    if required - g.keys():
        raise ValueError('La référence vidéo ne contient pas tous les types de questions requis')
    os.makedirs(a.sortie, exist_ok=True)
    dst = Path(a.sortie) / f"{fiche['identifiant']}.h5p"
    if dst.exists():
        raise FileExistsError('Sortie H5P existante : choisir une nouvelle destination')

    with tempfile.TemporaryDirectory() as tmp:
        extraire_bibliotheques(ref, tmp)
        c = os.path.join(tmp, "content")
        os.makedirs(c, exist_ok=True)
        content = contenu_questionnaire(fiche, ref_content, g) if questionnaire else \
            contenu_video(fiche, ref_content, g, c, projet, a.ffmpeg, a.affiches)
        h5p_json = dict(json.loads(ref.read("h5p.json")), title=fiche["titre_activite"])
        with open(os.path.join(c, "content.json"), "w", encoding="utf-8", newline='\n') as f:
            json.dump(content, f, ensure_ascii=False)
        with open(os.path.join(tmp, "h5p.json"), "w", encoding="utf-8", newline='\n') as f:
            json.dump(h5p_json, f, ensure_ascii=False)

        erreurs = verifier(tmp, h5p_json, content)
        if erreurs:
            sys.exit(f"{chemin_fiche} :\n" + "\n".join(erreurs))

        fd, publication = tempfile.mkstemp(prefix='.mcb-', suffix='.h5p', dir=dst.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(publication, "w") as z:
                for racine, dossiers, noms in os.walk(tmp):
                    dossiers.sort()
                    noms.sort()
                    for n in noms:
                        chemin = os.path.join(racine, n)
                        arc = os.path.relpath(chemin, tmp).replace(os.sep, "/")
                        mode = zipfile.ZIP_STORED if n.endswith((".mp4", ".jpg")) else zipfile.ZIP_DEFLATED
                        z.write(chemin, arc, compress_type=mode)
            taille = os.path.getsize(publication) / 2**20
            if a.limite_mio is not None and taille > a.limite_mio:
                raise ValueError(f'Paquet de {taille:.2f} Mio supérieur à la limite de {a.limite_mio} Mio')
            publier_nouveau(publication, dst)
        finally:
            Path(publication).unlink(missing_ok=True)

    taille = os.path.getsize(dst) / 2**20
    nb = len(fiche.get("interactions", fiche.get("questions", [])))
    print(f"{os.path.basename(dst)} : {taille:.1f} Mio ({nb} questions)")
    return dst


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fiches", nargs="+")
    p.add_argument("--mbz", required=True)
    p.add_argument('--reference-video', required=True, help='Motif non ambigu du nom du paquet vidéo dans le .mbz')
    p.add_argument('--reference-questionnaire', help='Motif non ambigu du paquet QuestionSet si nécessaire')
    p.add_argument('--projet', required=True, help='Racine explicite des chemins des médias dans les fiches')
    p.add_argument("--sortie", required=True)
    p.add_argument('--limite-mio', type=float, help='Taille maximale facultative ; refus au-delà, pas de changement de qualité silencieux')
    p.add_argument('--affiches', help='Dossier facultatif de posters existants nommés <identifiant>-affiche.jpg')
    p.add_argument('--langue-sous-titres', default='fr', help='Code de langue de repli des vidéos (fr par défaut)')
    p.add_argument('--libelle-sous-titres', help='Libellé de repli ; la fiche est prioritaire')
    p.add_argument("--ffmpeg", default=os.environ.get("FFMPEG_EXE") or shutil.which("ffmpeg"))
    a = p.parse_args()
    try:
        langue_sous_titres({}, a.langue_sous_titres, a.libelle_sous_titres)
    except ValueError as erreur:
        p.error(str(erreur))
    if not a.reference_video or a.limite_mio is not None and a.limite_mio <= 0:
        p.error('Motif vidéo non vide et limite positive attendus')
    with ExitStack() as stack:
        refs = {'video': stack.enter_context(paquet_reference(a.mbz, a.reference_video))}
        if a.reference_questionnaire:
            refs['questionnaire'] = stack.enter_context(paquet_reference(a.mbz, a.reference_questionnaire))
        for f in a.fiches:
            data = json.loads(Path(f).read_text(encoding='utf-8-sig'))
            if data.get('type') == 'QuestionSet' and 'questionnaire' not in refs:
                p.error('--reference-questionnaire requis pour un QuestionSet')
            construire(f, a, refs)


if __name__ == "__main__":
    main()
