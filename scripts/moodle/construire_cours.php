<?php
// Construit le cours décrit par cours/structure.json dans un Moodle (local de validation) avec les API natives.
//
// Usage : php construire_cours.php --moodle=<dossier config.php> --projet=<dossier du projet> --validation-locale [--categorie=1]
// Le cours est créé masqué. Une collision de nom abrégé est refusée, sans suppression.

define('CLI_SCRIPT', true);
$opts = getopt('', ['moodle:', 'projet:', 'categorie::', 'validation-locale']);
if (!isset($opts['validation-locale'])) {
    fwrite(STDERR, "Usage réservé à une instance locale de validation : ajouter --validation-locale.\n");
    exit(2);
}
require(rtrim($opts['moodle'], '/\\') . '/config.php');

require(__DIR__ . '/validation_locale.php');

require_once($CFG->libdir . '/clilib.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->libdir . '/completionlib.php');
require_once($CFG->dirroot . '/completion/criteria/completion_criteria_activity.php');
require_once($CFG->dirroot . '/completion/completion_aggregation.php');
require_once($CFG->libdir . '/resourcelib.php');

$projet = rtrim($opts['projet'], '/\\');
$categorie = (int)($opts['categorie'] ?? 1);
$s = json_decode(file_get_contents("$projet/cours/structure.json"), false, 512, JSON_THROW_ON_ERROR);
require_once(__DIR__ . '/activites_etendues.php');
try { mcb_valider_structure($s, $projet); }
catch (InvalidArgumentException $e) { fwrite(STDERR, "Construction refusée : " . $e->getMessage() . "\n"); exit(2); }
foreach ($s->sections as $sec) {
    foreach ($sec->activities as $a) {
        if (mcb_h5p_integre($a,$s->version ?? 1) && empty($CFG->allowstealth)) {
            fwrite(STDERR,"H5P intégré : les activités furtives doivent être autorisées dans cette instance locale avant construction.\n");
            exit(2);
        }
    }
}
foreach ($s->sections ?? [] as $section) {
    foreach ($section->activities ?? [] as $activity) {
        if (!in_array($activity->type ?? '', ['h5p', 'page', 'resource', 'book', 'assign', 'qbank', 'quiz', 'feedback', 'lesson', 'customcert','glossary'], true) ||
                (in_array($activity->type ?? '', ['feedback','customcert'], true) && ($s->version ?? 1) < 4)) {
            fwrite(STDERR, "Construction refusée : type non fabriqué par ce constructeur.\n");
            exit(2);
        }
    }
}
\core\session\manager::set_user(get_admin());
$fs = get_file_storage();
$usercontext = context_user::instance($USER->id);

function lire($projet, $relatif) {
    return file_get_contents("$projet/$relatif");
}

/** Dépose des fichiers dans une zone brouillon et retourne son identifiant. */
function brouillon(array $chemins) {
    global $fs, $usercontext, $s;
    $draftid = file_get_unused_draft_itemid();
    foreach ($chemins as $chemin) {
        $fs->create_file_from_pathname(['contextid' => $usercontext->id, 'component' => 'user', 'filearea' => 'draft',
            'itemid' => $draftid, 'filepath' => '/', 'filename' => basename($chemin),
            'author' => ($s->author ?? ''), 'license' => 'allrightsreserved'], $chemin);
    }
    return $draftid;
}

/** Réglages d'achèvement communs. */
function achevement($mi, $a) {
    $mi->completionexpected = 0;
    switch ($a->completion) {
        case 'manual':
            $mi->completion = COMPLETION_TRACKING_MANUAL;
            break;
        case 'view':
            $mi->completion = COMPLETION_TRACKING_AUTOMATIC;
            $mi->completionview = 1;
            break;
        case 'submit':
        case 'end':
            $mi->completion = COMPLETION_TRACKING_AUTOMATIC;
            break;
        case 'grade':
        case 'pass':
            $mi->completion = COMPLETION_TRACKING_AUTOMATIC;
            $mi->completionusegrade = 1;
            $mi->completiongradeitemnumber = 0;
            $mi->completionpassgrade = $a->completion === 'pass' ? 1 : 0;
            if ($a->completion === 'pass') {
                $mi->gradepass = $a->gradepass;
            }
            break;
        default:
            $mi->completion = COMPLETION_TRACKING_NONE;
    }
}

// 1. Cours neuf uniquement. Choisir un autre nom abrégé en cas de collision.
if ($ancien = $DB->get_record('course', ['shortname' => $s->shortname])) {
    fwrite(STDERR, "Construction refusée : un cours porte déjà ce nom abrégé.\n");
    exit(2);
}
$course = create_course((object)[
    'category' => $categorie, 'fullname' => $s->fullname, 'shortname' => $s->shortname,
    'summary' => $s->summary, 'summaryformat' => FORMAT_HTML, 'format' => 'topics',
    'numsections' => count($s->sections) - 1, 'visible' => 0, 'enablecompletion' => 1,
    'showcompletionconditions' => 1, 'showactivitydates' => 0, 'newsitems' => 0, 'showgrades' => 1,
    'startdate' => usergetmidnight(time()), 'enddate' => 0, 'lang' => '',
]);
$coursecontext = context_course::instance($course->id);
if (!empty($s->image)) { $fs->create_file_from_pathname(['contextid' => $coursecontext->id, 'component' => 'course', 'filearea' => 'overviewfiles',
    'itemid' => 0, 'filepath' => '/', 'filename' => basename($s->image), 'author' => ($s->author ?? '')], "$projet/$s->image"); }
echo "Cours créé : id $course->id ($s->shortname)\n";

// 2. Sections et activités.
$cmids = [];
foreach ($s->sections as $num => $sec) {
    $section = $DB->get_record('course_sections', ['course' => $course->id, 'section' => $num], '*', MUST_EXIST);
    course_update_section($course, $section, ['name' => $sec->name, 'summary' => lire($projet, $sec->summary),
        'summaryformat' => FORMAT_HTML]);
    foreach ($sec->activities as $a) {
        $mi = (object)['course' => $course->id, 'section' => $num, 'visible' => 1, 'name' => $a->name,
            'introeditor' => ['text' => $a->intro, 'format' => FORMAT_HTML, 'itemid' => file_get_unused_draft_itemid()],
            'showdescription' => 0, 'cmidnumber' => ($a->idnumber ?? '')];
        switch ($a->type) {
            case 'feedback':
            case 'lesson':
            case 'customcert':
                mcb_preparer_parcours($mi, $a);
                if ($a->type === 'customcert') {
                    $mi->availability = json_encode(mcb_availability_certificat($a,$course->id));
                }
                break;
            case 'qbank':
                $mi->modulename = 'qbank';
                $mi->type = 'standard';
                $mi->visible = 0;
                break;
            case 'glossary':
                mcb_preparer_glossaire($mi);
                break;
            case 'quiz':
                mcb_preparer_test($mi, $a);
                break;
            case 'book':
                $mi->modulename = 'book';
                $mi->numbering = 1;
                $mi->navstyle = 1;
                $mi->customtitles = 0;
                break;
            case 'assign':
                mcb_preparer_devoir($mi, $a);
                if (isset($a->attachments)) {
                    $mi->introattachments = brouillon(array_map(fn($file)=>"$projet/$file",$a->attachments));
                }
                break;
            case 'h5p':
                $mi->modulename = 'h5pactivity';
                $mi->packagefile = brouillon(["$projet/$a->package"]);
                $mi->grade = 100;
                $mi->grademethod = 1;
                $mi->enabletracking = 1;
                $mi->reviewmode = 1;
                $mi->displayoptions = 15;
                if (mcb_h5p_integre($a,$s->version ?? 1)) { $mi->visibleoncoursepage = 0; }
                break;
            case 'page':
                $mi->modulename = 'page';
                // Sans formulaire, page_add_instance lit « content » et n'enregistre pas les fichiers : voir plus bas.
                $images = array_map(fn($i) => "$projet/images-cours/$i", $a->images ?? []);
                $mi->content = lire($projet, $a->html);
                $mi->contentformat = FORMAT_HTML;
                $mi->display = RESOURCELIB_DISPLAY_OPEN;
                $mi->printintro = 0;
                $mi->printlastmodified = 0;
                $mi->printheading = 1;
                break;
            case 'resource':
                $mi->modulename = 'resource';
                $mi->files = brouillon(["$projet/$a->file"]);
                $mi->display = RESOURCELIB_DISPLAY_AUTO;
                $mi->printintro = 1;
                $mi->showsize = 1;
                $mi->showtype = 1;
                $mi->showdate = 0;
                $mi->filterfiles = 0;
                break;
        }
        $mi->module = $DB->get_field('modules', 'id', ['name' => $mi->modulename], MUST_EXIST);
        achevement($mi, $a);
        $cm = create_module($mi);
        if ($a->type === 'glossary') { mcb_finaliser_glossaire($cm,$a); }
        if (in_array($a->type, ['feedback','lesson','customcert'], true)) { mcb_finaliser_parcours($cm, $a, $projet); }
        if (in_array($a->type, ['qbank','quiz'], true)) { mcb_finaliser_test($cm, $a); }
        if (in_array($a->type, ['book','assign'], true)) { mcb_finaliser_activite($cm, $a, $projet); }
        if ($a->type === 'page' && $images) {
            file_save_draft_area_files(brouillon($images), context_module::instance($cm->coursemodule)->id,
                'mod_page', 'content', 0, ['subdirs' => 0]);
        }
        if ($a->course_required ?? ($a->completion !== 'none')) {
            $cmids[] = $cm->coursemodule;
        }
        echo "  [$num] $a->type : $a->name (cmid $cm->coursemodule)\n";
    }
    if (($s->version ?? 1) >= 5) {
        course_update_section($course,$section,['summary'=>mcb_resume_section($sec,$projet,$course->id,5),'summaryformat'=>FORMAT_HTML]);
    }
}

// 3. Achèvement du cours : toutes les activités suivies.
$criterion = new completion_criteria_activity();
$data = (object)['id' => $course->id, 'criteria_activity' => array_fill_keys($cmids, 1)];
$criterion->update_config($data);
$aggregation = new completion_aggregation(['course' => $course->id, 'criteriatype' => null]);
$aggregation->setMethod(COMPLETION_AGGREGATION_ALL);
$aggregation->save();
$aggregation = new completion_aggregation(['course' => $course->id, 'criteriatype' => COMPLETION_CRITERIA_TYPE_ACTIVITY]);
$aggregation->setMethod(COMPLETION_AGGREGATION_ALL);
$aggregation->save();

rebuild_course_cache($course->id, true);
echo "Achèvement du cours : " . count($cmids) . " activités requises.\nCOURSEID=$course->id\n";
