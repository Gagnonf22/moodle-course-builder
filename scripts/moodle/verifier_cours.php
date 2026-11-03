<?php
// Vérifie un cours restauré à partir de la sauvegarde : structure, achèvement, notes, fichiers.
//
// Usage : php verifier_cours.php --moodle=<dossier config.php> --courseid=<id> --projet=<dossier du projet>

define('CLI_SCRIPT', true);
$opts = getopt('', ['moodle:', 'courseid:', 'projet:', 'validation-locale', 'apprenants:']);
if (!isset($opts['validation-locale']) || empty($opts['moodle']) || empty($opts['projet']) ||
        !ctype_digit((string)($opts['courseid'] ?? '')) || (int)$opts['courseid'] < 1) {
    fwrite(STDERR, "Exiger --validation-locale --moodle --projet --courseid positif.\n");
    exit(2);
}
require(rtrim($opts['moodle'], '/\\') . '/config.php');
require(__DIR__ . '/validation_locale.php');
require_once($CFG->libdir . '/clilib.php');
require_once($CFG->libdir . '/gradelib.php');
require_once($CFG->libdir . '/completionlib.php');

$projet = rtrim($opts['projet'], '/\\');
$s = json_decode(file_get_contents("$projet/cours/structure.json"), false, 512, JSON_THROW_ON_ERROR);
if (!isset($s->sections) || !is_array($s->sections) || !in_array($s->version ?? 1, [1,2,3,4,5], true)) {
    fwrite(STDERR, "Contrat structure invalide.\n"); exit(2);
}
require_once(__DIR__ . '/activites_etendues.php');
try { mcb_valider_structure($s, $projet); }
catch (InvalidArgumentException $e) { fwrite(STDERR, "Contrat structure invalide : " . $e->getMessage() . "\n"); exit(2); }
$probes = isset($opts['apprenants']) ? json_decode(file_get_contents($opts['apprenants']), false, 512, JSON_THROW_ON_ERROR) : null;
$keys = [];
foreach ($s->sections as $num => $sec) {
    foreach ($sec->activities as $i => $a) {
        if (!in_array($a->type ?? '', ['h5p','page','resource','customcert','feedback','questionnaire','book','assign','qbank','quiz','lesson','glossary'], true) ||
                !in_array($a->completion ?? '', ['none','manual','view','grade','pass','submit','end'], true) ||
                ($a->completion === 'end' && $a->type !== 'lesson') ||
                ($a->completion === 'submit' && !in_array($a->type, ['feedback','assign','quiz'], true))) {
            fwrite(STDERR, "Type ou achèvement non géré.\n"); exit(2);
        }
        if (isset($a->idnumber)) {
            if (!is_string($a->idnumber) || $a->idnumber === '' || isset($keys[$a->idnumber])) {
                fwrite(STDERR, "Clé idnumber vide ou dupliquée.\n"); exit(2);
            }
            $keys[$a->idnumber] = [$num, $i, $a];
        }
    }
}
foreach ($s->sections as $sec) {
    foreach ($sec->activities as $a) {
        if ($a->type === 'customcert' && !isset($a->conditions) && (!isset($a->condition) || !isset($keys[$a->condition]) ||
                $keys[$a->condition][2]->completion !== 'pass' || !isset($a->idnumber))) {
            fwrite(STDERR, "Attestation : clé et condition de réussite requises.\n"); exit(2);
        }
    }
}
$course = get_course((int)$opts['courseid']);
$modinfo = get_fast_modinfo($course);
$fs = get_file_storage();
$erreurs = 0;
function verif($ok, $libelle) {
    global $erreurs;
    echo ($ok ? '  OK    ' : '  ÉCHEC ') . $libelle . "\n";
    if (!$ok) { $erreurs++; }
}

echo "Cours $course->id : « $course->fullname » ($course->shortname), format $course->format\n";
verif($course->visible == 0, 'cours masqué');
verif($course->enablecompletion == 1, 'suivi d\'achèvement activé');
$ctx = context_course::instance($course->id);
verif(count($fs->get_area_files($ctx->id, 'course', 'overviewfiles', 0, '', false)) == ($s->image_count ?? 1), 'nombre d’images du cours');

$attendu = 0;
foreach ($s->sections as $num => $sec) {
    $section = $modinfo->get_section_info($num);
    verif($section && $section->name === $sec->name, "section $num : $sec->name");
    if (($s->version ?? 1) >= 5) {
        verif($section && (int)$section->summaryformat === (int)FORMAT_HTML &&
            $section->summary === mcb_resume_section($sec,$projet,$course->id,5),'HTML riche et intégrations de la section');
    }
    $cms = array_values(array_filter(array_map(fn($id) => $modinfo->cms[$id], $modinfo->sections[$num] ?? [])));
    verif(count($cms) == count($sec->activities), "  " . count($cms) . " activité(s) sur " . count($sec->activities));
    foreach ($sec->activities as $i => $a) {
        $cm = $cms[$i] ?? null;
        if (!$cm || $cm->name !== $a->name) { verif(false, "  activité absente : $a->name"); continue; }
        $expectedtype = $a->type === 'h5p' ? 'h5pactivity' : $a->type;
        verif(($cm->modname ?? '') === $expectedtype, 'type de module');
        if (isset($a->idnumber)) { verif(($cm->idnumber ?? '') === $a->idnumber, 'clé idnumber'); }
        $cmctx = context_module::instance($cm->id);
        $att = ['none' => 0, 'manual' => 1, 'view' => 2, 'grade' => 2, 'pass' => 2, 'submit' => 2, 'end'=>2][$a->completion];
        $detail = "achèvement $cm->completion";
        $ok = $cm->completion == $att;
        if ($a->completion === 'view') { $ok = $ok && $cm->completionview == 1; }
        if ($a->completion === 'submit' && $a->type === 'quiz') {
            $ok = $ok && $cm->completiongradeitemnumber === null && (int)$cm->completionpassgrade === 0;
        }
        if (in_array($a->completion, ['grade', 'pass'])) {
            $ok = $ok && ($cm->completiongradeitemnumber === '0' || $cm->completiongradeitemnumber === 0);
            $ok = $ok && (int)$cm->completionpassgrade === ($a->completion === 'pass' ? 1 : 0);
            $detail .= ", note requise" . ($a->completion === 'pass' ? ' + réussite' : '');
        }
        if ($a->course_required ?? ($a->completion !== 'none')) { $attendu++; }
        if ($a->type === 'glossary') {
            $ok = $ok && mcb_verifier_glossaire($cm,$a);
            $detail .= ', termes et définitions du Glossaire';
        } elseif ($a->type === 'lesson') {
            $ok = $ok && mcb_verifier_parcours($cm, $a, $projet);
            $detail .= ', pages et sauts de Leçon v4';
        } elseif (in_array($a->type, ['qbank','quiz'], true)) {
            $ok = $ok && mcb_verifier_test($cm, $a, $course->id);
            $detail .= ', banque et test natif v3';
        } elseif (in_array($a->type, ['book','assign'], true)) {
            $ok = $ok && mcb_verifier_etendue($cm, $a, $projet, $course->id);
            $detail .= ', contenu et configuration v2';
        } elseif ($a->type === 'h5p') {
            if (mcb_h5p_integre($a,$s->version ?? 1)) {
                $ok = $ok && (int)$cm->visible === 1 && (int)$cm->visibleoncoursepage === 0;
            }
            $f = array_values($fs->get_area_files($cmctx->id, 'mod_h5pactivity', 'package', 0, '', false));
            $hash = $f ? $f[0]->get_contenthash() : '';
            $okfichier = $hash === sha1_file("$projet/$a->package");
            $gi = grade_item::fetch(['courseid' => $course->id, 'itemmodule' => 'h5pactivity', 'iteminstance' => $cm->instance]);
            $detail .= sprintf(", paquet %s (%.1f Mio), note /%d, seuil %d", $okfichier ? 'identique' : 'DIFFÉRENT',
                $f ? $f[0]->get_filesize() / 1048576 : 0, $gi ? $gi->grademax : -1, $gi ? $gi->gradepass : -1);
            $ok = $ok && $okfichier && $gi && (float)$gi->grademax == 100.0
                && (float)$gi->gradepass == (float)($a->gradepass ?? 0);
        } elseif ($a->type === 'page') {
            $page = $DB->get_record('page', ['id' => $cm->instance]);
            $imgs = $fs->get_area_files($cmctx->id, 'mod_page', 'content', 0, '', false);
            $okimg = count($imgs) == count($a->images ?? []);
            foreach ($a->images ?? [] as $img) {
                $okimg = $okimg && strpos($page->content, "@@PLUGINFILE@@/$img") !== false;
            }
            $detail .= ', ' . count($imgs) . ' image(s)';
            $ok = $ok && $okimg && strlen($page->content) > 200;
        } elseif ($a->type === 'resource') {
            $f = array_values($fs->get_area_files($cmctx->id, 'mod_resource', 'content', 0, '', false));
            $ok = $ok && $f && $f[0]->get_contenthash() === sha1_file("$projet/$a->file");
            $detail .= ', fichier ' . ($f ? $f[0]->get_filename() : 'absent');
        } elseif (in_array($a->type, ['customcert', 'feedback', 'questionnaire'], true)) {
            $record = $DB->get_record($a->type, ['id' => $cm->instance, 'course' => $course->id]);
            $ok = $ok && (bool)$record;
            if (($s->version ?? 1) >= 4 && in_array($a->type, ['feedback','customcert'], true)) {
                $ok = $ok && mcb_verifier_parcours($cm, $a, $projet);
            }
            if ($a->completion === 'submit') { $ok = $ok && !empty($record->completionsubmit); }
            if ($a->type !== 'customcert') {
                $ok = $ok && json_decode($cm->availability ?? 'null') == ($a->availability ?? null);
            }
            if ($a->type === 'customcert') {
                if (isset($a->conditions)) {
                    $ok = $ok && json_decode($cm->availability ?? 'null') == mcb_availability_certificat($a,$course->id);
                    mcb_verifier_acces_v5($cm,$course,$probes);
                    verif($ok,"  $a->type : conditions multiples et contenu");
                    continue;
                }
                [$cn, $ci, $cond] = $keys[$a->condition];
                $conditionid = null;
                foreach ($modinfo->sections[$cn] ?? [] as $candidateid) {
                    $candidate = $modinfo->cms[$candidateid];
                    if (($candidate->idnumber ?? '') === $a->condition) { $conditionid = $candidate->id; }
                }
                $state = $a->condition_state ?? 1;
                $expected = (object)['op'=>'&', 'c'=>[(object)['type'=>'completion', 'cm'=>$conditionid, 'e'=>$state]], 'showc'=>[true]];
                $ok = $ok && $conditionid !== null && in_array($state, [1,2], true) &&
                    json_decode($cm->availability ?? 'null') == $expected;
                // Les deux états ne peuvent être attestés par une inspection statique.
                foreach (['echec'=>3, 'reussite'=>2] as $label=>$completionstate) {
                    $uid = $probes->$label ?? null;
                    if (!is_int($uid) || $uid < 1 || ($probes->echec ?? null) === ($probes->reussite ?? null)) {
                        verif(false, "attestation $label : compte d’essai distinct manquant (À valider)");
                        continue;
                    }
                    $learnerctx = context_course::instance($course->id);
                    if (!is_enrolled($learnerctx, $uid, '', true) || is_siteadmin($uid) ||
                            has_capability('moodle/course:manageactivities', $learnerctx, $uid) ||
                            has_capability('moodle/course:ignoreavailabilityrestrictions', context_module::instance($cm->id), $uid)) {
                        verif(false, "attestation $label : compte non apprenant ou non inscrit"); continue;
                    }
                    $data = $DB->get_record('course_modules_completion', ['coursemoduleid'=>$conditionid, 'userid'=>$uid]);
                    verif($data && (int)$data->completionstate === $completionstate, "attestation $label : état réel de l’évaluation");
                    $mi = get_fast_modinfo($course, $uid);
                    $info = new \core_availability\info_module($mi->get_cm($cm->id));
                    $why = '';
                    $allowed = $info->is_available($why, false, $uid);
                    verif($allowed === ($label === 'reussite'), "attestation $label : restriction évaluée par Moodle");
                }
                $detail .= ', PDF et navigation à vérifier dans le navigateur';
            }
        }
        verif($ok, "  $a->type « $a->name » : $detail");
    }
}

$criteres = $DB->count_records('course_completion_criteria', ['course' => $course->id,
    'criteriatype' => COMPLETION_CRITERIA_TYPE_ACTIVITY]);
verif($criteres == $attendu, "achèvement du cours : $criteres activités requises (attendu $attendu)");
$users = $DB->count_records_sql("SELECT COUNT(1) FROM {user_enrolments} ue JOIN {enrol} e ON e.id = ue.enrolid
                                 WHERE e.courseid = ?", [$course->id]);
if ($probes === null) { verif($users == 0, "aucun utilisateur inscrit ($users)"); }
else { echo "  INFO  Comptes d’essai présents ; aucun export de leurs données par ce vérificateur.\n"; }
echo $erreurs ? "RÉSULTAT : $erreurs échec(s)\n" : "RÉSULTAT : toutes les vérifications réussies\n";

exit($erreurs ? 1 : 0);
