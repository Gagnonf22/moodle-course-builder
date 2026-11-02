<?php
// Contrat v2 : Livre et Devoir. Fonctions chargées après le garde-fou local par les CLI.
require_once(__DIR__ . '/tests_natifs.php');
require_once(__DIR__ . '/parcours_retroaction.php');

/** Lit un contenu du projet, sans sortie de sa racine. */
function mcb_contenu(string $projet, string $chemin): string {
    $base = realpath($projet);
    $file = realpath($projet . '/' . $chemin);
    if (!$base || !$file || !is_file($file) ||
            !str_starts_with(str_replace('\\', '/', $file), str_replace('\\', '/', $base) . '/')) {
        throw new InvalidArgumentException('Fichier de contenu absent ou hors projet.');
    }
    return file_get_contents($file);
}

/** Vérifie les nouvelles capacités avant toute création. V1 conserve son contrat historique. */
function mcb_valider_structure($s, string $projet): void {
    if (!is_object($s) || !in_array($s->version ?? 1, [1, 2, 3, 4], true) || !is_array($s->sections ?? null)) {
        throw new InvalidArgumentException('Version ou sections du contrat invalides.');
    }
    $keys = [];
    foreach ($s->sections as $sec) {
        foreach ($sec->activities ?? [] as $a) {
            if (($s->version ?? 1) === 1 && in_array($a->type ?? '', ['book', 'assign'], true)) {
                throw new InvalidArgumentException('Livre et Devoir exigent le contrat version 2.');
            }
            if (($s->version ?? 1) < 2) { continue; }
            if (!is_string($a->idnumber ?? null) || trim($a->idnumber) === '' || isset($keys[$a->idnumber])) {
                throw new InvalidArgumentException('Version 2 : idnumber unique et non vide requis.');
            }
            $keys[$a->idnumber] = true;
            if (!in_array($a->completion ?? '', ['none','manual','view','grade','pass','submit','end'], true) ||
                    ($a->completion === 'end' && $a->type !== 'lesson')) {
                throw new InvalidArgumentException('Mode d’achèvement inconnu.');
            }
            if ($a->type === 'book') {
                if (!in_array($a->completion, ['none','manual','view'], true) || empty($a->chapters) || !is_array($a->chapters)) {
                    throw new InvalidArgumentException('Livre : chapitres et achèvement de consultation requis.');
                }
                foreach ($a->chapters as $i => $ch) {
                    if (!is_string($ch->title ?? null) || trim($ch->title) === '' ||
                            !is_string($ch->html ?? null) || !is_bool($ch->subchapter ?? false) ||
                            ($i === 0 && ($ch->subchapter ?? false))) {
                        throw new InvalidArgumentException('Chapitre invalide ou premier chapitre secondaire.');
                    }
                    mcb_contenu($projet, $ch->html);
                }
            } elseif ($a->type === 'assign') {
                if (!is_object($a->submission ?? null) || !is_bool($a->submission->text ?? false) ||
                        !is_bool($a->submission->files ?? false) ||
                        !(($a->submission->text ?? false) || ($a->submission->files ?? false)) ||
                        !in_array($a->completion, ['none','manual','grade','pass','submit'], true)) {
                    throw new InvalidArgumentException('Devoir : remise texte et/ou fichier, mode compatible requis.');
                }
                $max = $a->grade ?? null;
                $pass = $a->gradepass ?? 0;
                if (!is_numeric($max) || $max <= 0 || !is_numeric($pass) || $pass < 0 || $pass > $max ||
                        ($a->completion === 'pass' && $pass <= 0) ||
                        !is_int($a->submission->maxfiles ?? 1) || ($a->submission->maxfiles ?? 1) < 1 ||
                        !is_int($a->submission->maxbytes ?? 1048576) || ($a->submission->maxbytes ?? 1048576) < 1) {
                    throw new InvalidArgumentException('Devoir : note, seuil ou limites de remise invalides.');
                }
                mcb_definition($a); // Valide également les critères avant toute écriture.
            }
        }
    }
    mcb_valider_tests($s);
    mcb_valider_parcours($s, $projet);
}

/** Transforme la description synthétique en données attendues par le contrôleur Moodle. */
function mcb_definition($a): array {
    $g = $a->grading ?? null;
    if (!is_object($g) || !in_array($g->method ?? '', ['rubric','guide'], true) ||
            !is_string($g->name ?? null) || trim($g->name) === '' ||
            !is_array($g->criteria ?? null) || !$g->criteria) {
        throw new InvalidArgumentException('Guide ou grille avec nom et critères requis.');
    }
    $criteria = [];
    foreach ($g->criteria as $i => $c) {
        if (!is_string($c->description ?? null) || trim($c->description) === '') {
            throw new InvalidArgumentException('Description du critère requise.');
        }
        $row = ['sortorder'=>$i, 'description'=>$c->description, 'descriptionformat'=>1];
        if ($g->method === 'guide') {
            if (!is_numeric($c->maxscore ?? null) || $c->maxscore <= 0) {
                throw new InvalidArgumentException('Maximum positif du critère requis.');
            }
            $row += ['shortname'=>$c->shortname ?? ('Critère ' . ($i + 1)),
                'descriptionmarkers'=>$c->markers ?? '', 'descriptionmarkersformat'=>1, 'maxscore'=>$c->maxscore];
        } else {
            if (!is_array($c->levels ?? null) || count($c->levels) < 2) {
                throw new InvalidArgumentException('Au moins deux niveaux requis par critère.');
            }
            $scores = [];
            foreach ($c->levels as $j => $l) {
                if (!is_numeric($l->score ?? null) || $l->score < 0 ||
                        !is_string($l->definition ?? null) || trim($l->definition) === '' ||
                        in_array((float)$l->score, $scores, true)) {
                    throw new InvalidArgumentException('Niveaux : scores distincts positifs ou nuls et textes requis.');
                }
                $scores[] = (float)$l->score;
                $row['levels']['NEWID' . ($j + 1)] = ['score'=>$l->score,
                    'definition'=>$l->definition, 'definitionformat'=>1];
            }
            if (min($scores) !== 0.0 || max($scores) <= 0) {
                throw new InvalidArgumentException('Grille : niveau zéro et maximum positif requis.');
            }
        }
        $criteria['NEWID' . ($i + 1)] = $row;
    }
    return $criteria;
}

/** Champs nécessaires à assign_add_instance et aux plugins de remise. */
function mcb_preparer_devoir($mi, $a): void {
    $mi->modulename = 'assign';
    foreach (['submissiondrafts','requiresubmissionstatement','sendnotifications','sendlatenotifications',
            'sendstudentnotifications','duedate','cutoffdate','gradingduedate','allowsubmissionsfromdate',
            'teamsubmission','requireallteammemberssubmit','blindmarking','markingworkflow','markingallocation'] as $k) {
        $mi->$k = 0;
    }
    $mi->alwaysshowdescription = 1;
    $mi->grade = $a->grade;
    $mi->gradepass = $a->gradepass ?? 0;
    $mi->maxattempts = 1;
    $mi->attemptreopenmethod = 'none';
    $mi->completionsubmit = $a->completion === 'submit' ? 1 : 0;
    $mi->assignsubmission_onlinetext_enabled = (int)($a->submission->text ?? false);
    $mi->assignsubmission_onlinetext_wordlimitenabled = 0;
    $mi->assignsubmission_onlinetext_wordlimit = 0;
    $mi->assignsubmission_file_enabled = (int)($a->submission->files ?? false);
    $mi->assignsubmission_file_maxfiles = $a->submission->maxfiles ?? 1;
    $mi->assignsubmission_file_maxsizebytes = $a->submission->maxbytes ?? 1048576;
    $mi->assignsubmission_file_filetypes = '';
    $mi->assignfeedback_comments_enabled = 1;
    $mi->assignfeedback_comments_commentinline = 0;
    $mi->assignfeedback_file_enabled = 0;
    $mi->assignfeedback_editpdf_enabled = 0;
    $mi->assignfeedback_offline_enabled = 0;
    $mi->advancedgradingmethod_submissions = $a->grading->method;
}

/** Complète le module neuf par ses chapitres ou sa définition de correction. */
function mcb_finaliser_activite($cm, $a, string $projet): void {
    global $DB, $CFG;
    if ($a->type === 'book') {
        require_once($CFG->dirroot . '/mod/book/locallib.php');
        $book = $DB->get_record('book', ['id'=>$cm->instance], '*', MUST_EXIST);
        foreach ($a->chapters as $i => $ch) {
            $chapter = (object)['bookid'=>$cm->instance, 'pagenum'=>$i + 1,
                'subchapter'=>(int)($ch->subchapter ?? false), 'title'=>$ch->title,
                'content'=>mcb_contenu($projet, $ch->html), 'contentformat'=>FORMAT_HTML,
                'hidden'=>0, 'timecreated'=>time(), 'timemodified'=>time(), 'importsrc'=>''];
            $chapter->id = $DB->insert_record('book_chapters', $chapter);
            $DB->set_field('book', 'revision', ++$book->revision, ['id'=>$book->id]);
            \mod_book\event\chapter_created::create_from_chapter($book,
                context_module::instance($cm->coursemodule), $chapter)->trigger();
            book_preload_chapters($book);
        }
    } elseif ($a->type === 'assign') {
        require_once($CFG->dirroot . '/grade/grading/lib.php');
        $manager = get_grading_manager(context_module::instance($cm->coursemodule), 'mod_assign', 'submissions');
        $manager->set_active_method($a->grading->method);
        $controller = $manager->get_controller($a->grading->method);
        $definition = (object)['name'=>$a->grading->name,
            'description_editor'=>['text'=>$a->grading->description ?? '', 'format'=>FORMAT_HTML,
                'itemid'=>file_get_unused_draft_itemid()],
            'status'=>gradingform_controller::DEFINITION_STATUS_READY];
        $method = $a->grading->method;
        $definition->$method = ['criteria'=>mcb_definition($a)];
        $controller->update_definition($definition);
    }
}

/** Vérifie contenu, plugins de remise, seuil et définition, indépendamment des identifiants restaurés. */
function mcb_verifier_etendue($cm, $a, string $projet, int $courseid): bool {
    global $DB, $CFG;
    if ($a->type === 'book') {
        $chapters = array_values($DB->get_records('book_chapters', ['bookid'=>$cm->instance], 'pagenum ASC'));
        if (count($chapters) !== count($a->chapters)) { return false; }
        foreach ($a->chapters as $i => $ch) {
            if ($chapters[$i]->title !== $ch->title ||
                    (bool)$chapters[$i]->subchapter !== ($ch->subchapter ?? false) ||
                    $chapters[$i]->content !== mcb_contenu($projet, $ch->html) || (int)$chapters[$i]->hidden !== 0) { return false; }
        }
        return true;
    }
    require_once($CFG->dirroot . '/mod/assign/locallib.php');
    require_once($CFG->dirroot . '/grade/grading/lib.php');
    $assign = new assign(context_module::instance($cm->id), $cm, get_course($courseid));
    $record = $assign->get_instance();
    $gi = grade_item::fetch(['courseid'=>$courseid,'itemmodule'=>'assign','iteminstance'=>$cm->instance]);
    if (!$gi || (float)$gi->grademax !== (float)$a->grade || (float)$gi->gradepass !== (float)($a->gradepass ?? 0) ||
            $record->intro !== $a->intro || (int)$record->completionsubmit !== ($a->completion === 'submit' ? 1 : 0) ||
            (bool)$assign->get_submission_plugin_by_type('onlinetext')->is_enabled() !== ($a->submission->text ?? false) ||
            (bool)$assign->get_submission_plugin_by_type('file')->is_enabled() !== ($a->submission->files ?? false)) { return false; }
    if ($a->submission->files ?? false) {
        $file = $assign->get_submission_plugin_by_type('file');
        if ((int)$file->get_config('maxfilesubmissions') !== ($a->submission->maxfiles ?? 1) ||
                (int)$file->get_config('maxsubmissionsizebytes') !== ($a->submission->maxbytes ?? 1048576)) { return false; }
    }
    $manager = get_grading_manager(context_module::instance($cm->id), 'mod_assign', 'submissions');
    $method = $a->grading->method;
    if ($manager->get_active_method() !== $method) { return false; }
    $controller = $manager->get_controller($method);
    if (!$controller->is_form_available()) { return false; }
    $definition = $controller->get_definition();
    if ($definition->name !== $a->grading->name) { return false; }
    $field = $method . '_criteria';
    $actual = array_values($definition->$field);
    $expected = array_values(mcb_definition($a));
    if (count($actual) !== count($expected)) { return false; }
    foreach ($expected as $i => $row) {
        foreach ($row as $k => $value) {
            if ($k === 'levels') {
                $levels = array_values($actual[$i]['levels']);
                if (count($levels) !== count($value)) { return false; }
                foreach (array_values($value) as $j => $level) {
                    if ((float)$levels[$j]['score'] !== (float)$level['score'] ||
                            $levels[$j]['definition'] !== $level['definition']) { return false; }
                }
            } elseif ((string)$actual[$i][$k] !== (string)$value) { return false; }
        }
    }
    return true;
}
