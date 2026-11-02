<?php
// Contrat v3 : banque qbank et test natif ; aucune API de test PHPUnit utilisée en exécution.

function mcb_nombre($value): bool {
    return (is_int($value) || is_float($value)) && is_finite((float)$value);
}

/** Contrat explicite, sans conversion silencieuse d'un type ou d'un barème. */
function mcb_valider_questions($a): void {
    if ($a->completion !== 'none' || ($a->course_required ?? false) !== false ||
            !is_array($a->questions ?? null) || !$a->questions) {
        throw new InvalidArgumentException('Banque : questions requises, sans achèvement ni critère de cours.');
    }
    $keys = [];
    foreach ($a->questions as $q) {
        if (!is_object($q) || !is_string($q->key ?? null) || trim($q->key) === '' || isset($keys[$q->key]) ||
                !in_array($q->type ?? '', ['multichoice','truefalse','shortanswer','numerical'], true) ||
                !is_string($q->name ?? null) || trim($q->name) === '' ||
                !is_string($q->text ?? null) || trim($q->text) === '' ||
                !mcb_nombre($q->mark ?? null) || $q->mark <= 0 ||
                !is_string($q->generalfeedback ?? '')) {
            throw new InvalidArgumentException('Question : clé unique, type pris en charge, textes et points positifs requis.');
        }
        $keys[$q->key] = true;
        if ($q->type === 'truefalse') {
            if (!is_bool($q->correct ?? null) || !is_string($q->feedbacktrue ?? '') || !is_string($q->feedbackfalse ?? '')) {
                throw new InvalidArgumentException('Vrai/faux : bonne réponse booléenne et rétroactions requises.');
            }
            continue;
        }
        if (!is_array($q->answers ?? null) || count($q->answers) < ($q->type === 'multichoice' ? 2 : 1) ||
                ($q->type === 'multichoice' && (!is_bool($q->single ?? null) || !is_bool($q->shuffle ?? false))) ||
                ($q->type === 'shortanswer' && !is_bool($q->usecase ?? false))) {
            throw new InvalidArgumentException('Question : réponses et options invalides.');
        }
        $positive = 0.0; $max = -1; $full = 0;
        foreach ($q->answers as $answer) {
            if (!is_string($answer->text ?? null) || trim($answer->text) === '' ||
                    !mcb_nombre($answer->fraction ?? null) || $answer->fraction < -1 || $answer->fraction > 1 ||
                    !is_string($answer->feedback ?? '')) {
                throw new InvalidArgumentException('Réponse : texte, fraction entre -1 et 1 et rétroaction requis.');
            }
            if ($q->type === 'numerical' && (!is_numeric($answer->text) || !is_finite((float)$answer->text) ||
                    !mcb_nombre($answer->tolerance ?? null) || $answer->tolerance < 0)) {
                throw new InvalidArgumentException('Numérique : réponse numérique finie et tolérance positive ou nulle requises.');
            }
            $positive += max(0, $answer->fraction); $max = max($max, $answer->fraction);
            if ($answer->fraction == 1) { $full++; }
        }
        if (($q->type === 'multichoice' && !$q->single && abs($positive - 1) > 0.000001) ||
                ($q->type === 'multichoice' && $q->single && ($full !== 1 || $positive != 1)) ||
                ($q->type !== 'multichoice' && $max != 1)) {
            throw new InvalidArgumentException('Barème : bonne réponse complète ou somme positive de choix multiple égale à 1 requise.');
        }
    }
}

/** Relecture : phases et champs connus seulement ; sortie conforme aux noms des champs du formulaire. */
function mcb_relecture($review): array {
    $phases = ['during','immediately','open','closed'];
    $fields = ['attempt','correctness','maxmarks','marks','specificfeedback','generalfeedback','rightanswer','overallfeedback'];
    if (!is_object($review)) { throw new InvalidArgumentException('Réglages de relecture explicites requis.'); }
    foreach ($review as $phase => $values) {
        if (!in_array($phase, $phases, true) || !is_object($values)) { throw new InvalidArgumentException('Phase de relecture inconnue.'); }
        foreach ($values as $field => $value) {
            if (!in_array($field, $fields, true) || !is_bool($value)) { throw new InvalidArgumentException('Champ de relecture inconnu ou non booléen.'); }
        }
    }
    $out = [];
    foreach ($phases as $phase) {
        foreach ($fields as $field) { $out[$field . $phase] = (int)($review->$phase->$field ?? false); }
    }
    if (!$out['attemptduring'] || $out['overallfeedbackduring']) {
        throw new InvalidArgumentException('Relecture : tentative visible pendant, rétroaction globale seulement après.');
    }
    return $out;
}

function mcb_valider_tests($s): void {
    $banks = []; $quizzes = [];
    foreach ($s->sections as $sec) {
        foreach ($sec->activities ?? [] as $a) {
            if (!in_array($a->type ?? '', ['qbank','quiz'], true)) { continue; }
            if (($s->version ?? 1) < 3) { throw new InvalidArgumentException('Banque et test natif exigent version 3 ou supérieure.'); }
            if ($a->type === 'qbank') { mcb_valider_questions($a); $banks[$a->idnumber] = $a; }
            else {
                if (!isset($banks[$a->bank ?? '']) || !is_array($a->questions ?? null) || !$a->questions ||
                        count($a->questions) !== count(array_unique($a->questions)) ||
                        !is_int($a->attempts ?? null) || $a->attempts < 1 ||
                        !in_array($a->grademethod ?? '', ['highest','average','first','last'], true) ||
                        !mcb_nombre($a->grade ?? null) || $a->grade <= 0 ||
                        !mcb_nombre($a->gradepass ?? null) || $a->gradepass < 0 || $a->gradepass > $a->grade ||
                        !in_array($a->completion, ['none','manual','grade','pass'], true) ||
                        ($a->completion === 'pass' && $a->gradepass <= 0)) {
                    throw new InvalidArgumentException('Test : banque précédente, questions uniques, tentatives, méthode et seuil valides requis.');
                }
                $questions = array_column($banks[$a->bank]->questions, null, 'key');
                foreach ($a->questions as $key) {
                    if (!is_string($key) || !isset($questions[$key])) { throw new InvalidArgumentException('Question référencée absente de la banque.'); }
                }
                mcb_relecture($a->review ?? null);
            }
        }
    }
}

/** Données du formulaire natif qtype ; les ressources externes ne sont pas importées ici. */
function mcb_form_question($q, int $category): object {
    $html = fn($text) => ['text'=>$text,'format'=>1];
    $f = (object)['category'=>(string)$category, 'name'=>$q->name, 'idnumber'=>$q->key,
        'questiontext'=>$html($q->text), 'generalfeedback'=>$html($q->generalfeedback ?? ''),
        'defaultmark'=>$q->mark, 'penalty'=>0, 'status'=>'ready', 'hint'=>[]];
    if ($q->type === 'truefalse') {
        $f->correctanswer = (int)$q->correct;
        $f->feedbacktrue = $html($q->feedbacktrue ?? '');
        $f->feedbackfalse = $html($q->feedbackfalse ?? '');
        $f->showstandardinstruction = 0;
        return $f;
    }
    foreach ($q->answers as $answer) {
        $f->answer[] = $q->type === 'multichoice' ? $html($answer->text) : $answer->text;
        $f->fraction[] = $answer->fraction;
        $f->feedback[] = $html($answer->feedback ?? '');
        if ($q->type === 'numerical') { $f->tolerance[] = (string)$answer->tolerance; }
    }
    if ($q->type === 'multichoice') {
        $f->single = (int)$q->single; $f->shuffleanswers = (int)($q->shuffle ?? false);
        $f->answernumbering = 'abc'; $f->shownumcorrect = 0; $f->showstandardinstruction = 0;
        foreach (['correctfeedback','partiallycorrectfeedback','incorrectfeedback'] as $k) { $f->$k = $html(''); }
    } elseif ($q->type === 'shortanswer') { $f->usecase = (int)($q->usecase ?? false); }
    else { $f->unit = []; $f->multiplier = []; $f->unitrole = 0; $f->unitpenalty = 0; $f->unitsleft = 0; }
    return $f;
}

function mcb_preparer_test($mi, $a): void {
    $mi->modulename = 'quiz';
    foreach (['timeopen','timeclose','attemptonlast','sumgrades','timelimit','graceperiod','delay1','delay2',
            'showuserpicture','showblocks','completionattemptsexhausted','completionminattempts'] as $k) { $mi->$k = 0; }
    $mi->preferredbehaviour = 'deferredfeedback'; $mi->attempts = $a->attempts;
    $mi->grademethod = ['highest'=>1,'average'=>2,'first'=>3,'last'=>4][$a->grademethod];
    $mi->grade = $a->grade; $mi->gradepass = $a->gradepass;
    $mi->decimalpoints = 2; $mi->questiondecimalpoints = -1;
    $mi->questionsperpage = 1; $mi->shuffleanswers = 0;
    $mi->overduehandling = 'autosubmit'; $mi->quizpassword = ''; $mi->subnet = ''; $mi->browsersecurity = '';
    $mi->navmethod = 'free';
    foreach (mcb_relecture($a->review) as $key=>$value) { $mi->$key = $value; }
}

/** Questions prêtes de la dernière version, limitées au contexte du module banque. */
function mcb_questions_banque(int $contextid): array {
    global $DB;
    $records = $DB->get_records_sql("SELECT q.id, e.idnumber, qv.questionbankentryid
        FROM {question} q JOIN {question_versions} qv ON qv.questionid=q.id
        JOIN {question_bank_entries} e ON e.id=qv.questionbankentryid
        JOIN {question_categories} c ON c.id=e.questioncategoryid
        WHERE c.contextid=? AND qv.status='ready'
          AND qv.version=(SELECT MAX(v.version) FROM {question_versions} v WHERE v.questionbankentryid=e.id)", [$contextid]);
    $out = [];
    foreach ($records as $q) { $out[$q->idnumber] = $q; }
    return $out;
}

function mcb_banque_cours(int $courseid, string $key) {
    foreach (get_fast_modinfo($courseid)->cms as $cm) {
        if ($cm->modname === 'qbank' && $cm->idnumber === $key) { return $cm; }
    }
    throw new RuntimeException('Module de banque introuvable.');
}

function mcb_finaliser_test($cm, $a): void {
    global $CFG, $DB;
    require_once($CFG->libdir . '/questionlib.php');
    if ($a->type === 'qbank') {
        $context = context_module::instance($cm->coursemodule);
        $category = question_get_default_category($context->id, true);
        foreach ($a->questions as $q) {
            $saved = question_bank::get_qtype($q->type)->save_question((object)['qtype'=>$q->type], mcb_form_question($q, $category->id));
            if (!empty($saved->errors)) { throw new RuntimeException('Question refusée par son type natif.'); }
        }
    } else {
        require_once($CFG->dirroot . '/mod/quiz/locallib.php');
        $quiz = $DB->get_record('quiz', ['id'=>$cm->instance], '*', MUST_EXIST);
        $quiz->cmid = $cm->coursemodule;
        rebuild_course_cache($quiz->course, true);
        $bank = mcb_banque_cours($quiz->course, $a->bank);
        $questions = mcb_questions_banque(context_module::instance($bank->id)->id);
        foreach ($a->questions as $key) {
            // Le succès natif n'a pas de valeur de retour ; seul false signifie doublon/refus.
            if (!isset($questions[$key]) || quiz_add_quiz_question($questions[$key]->id, $quiz) === false) {
                throw new RuntimeException('Ajout de question au test refusé.');
            }
        }
        \mod_quiz\quiz_settings::create($quiz->id)->get_grade_calculator()->recompute_quiz_sumgrades();
    }
}

function mcb_question_identique($q, $expected): bool {
    global $DB;
    $raw = $DB->get_record('question', ['id'=>$q->id], '*', MUST_EXIST);
    if ($raw->qtype !== $expected->type || $raw->name !== trim($expected->name) ||
            $raw->questiontext !== trim($expected->text) || $raw->generalfeedback !== trim($expected->generalfeedback ?? '') ||
            (float)$raw->defaultmark !== (float)$expected->mark) { return false; }
    $loaded = question_bank::load_question($q->id);
    if ($expected->type === 'truefalse') {
        return $loaded->rightanswer === $expected->correct && $loaded->truefeedback === ($expected->feedbacktrue ?? '') &&
            $loaded->falsefeedback === ($expected->feedbackfalse ?? '');
    }
    $answers = array_values($loaded->answers);
    if (count($answers) !== count($expected->answers)) { return false; }
    foreach ($expected->answers as $i=>$ans) {
        if ($answers[$i]->answer !== trim($ans->text) || abs($answers[$i]->fraction - $ans->fraction) > 0.000001 ||
                $answers[$i]->feedback !== ($ans->feedback ?? '')) { return false; }
        if ($expected->type === 'numerical' && abs($answers[$i]->tolerance - $ans->tolerance) > 0.000001) { return false; }
    }
    if ($expected->type === 'multichoice') {
        $option = $DB->get_record('qtype_multichoice_options', ['questionid'=>$q->id], '*', MUST_EXIST);
        return (bool)$option->single === $expected->single && (bool)$option->shuffleanswers === ($expected->shuffle ?? false);
    }
    if ($expected->type === 'shortanswer') { return (bool)$loaded->usecase === ($expected->usecase ?? false); }
    $numerical = $DB->get_record('question_numerical_options', ['question'=>$q->id], '*', MUST_EXIST);
    if ((int)$numerical->showunits !== 0 || $DB->count_records('question_numerical_units', ['question'=>$q->id]) !== 0) { return false; }
    return true;
}

function mcb_verifier_test($cm, $a, int $courseid): bool {
    global $DB, $CFG;
    require_once($CFG->libdir . '/questionlib.php');
    if ($a->type === 'qbank') {
        $record = $DB->get_record('qbank', ['id'=>$cm->instance], '*', MUST_EXIST);
        if ($record->type !== 'standard') { return false; }
        $questions = mcb_questions_banque(context_module::instance($cm->id)->id);
        if (count($questions) !== count($a->questions) || (int)$cm->completion !== 0 || (int)$cm->visible !== 0) { return false; }
        foreach ($a->questions as $expected) {
            if (!isset($questions[$expected->key]) || !mcb_question_identique($questions[$expected->key], $expected)) { return false; }
        }
        return true;
    }
    require_once($CFG->dirroot . '/mod/quiz/locallib.php');
    $quiz = $DB->get_record('quiz', ['id'=>$cm->instance], '*', MUST_EXIST);
    $gi = grade_item::fetch(['courseid'=>$courseid,'itemmodule'=>'quiz','iteminstance'=>$cm->instance]);
    if (!$gi || (float)$gi->grademax !== (float)$a->grade || (float)$gi->gradepass !== (float)$a->gradepass ||
            (int)$quiz->attempts !== $a->attempts || (int)$quiz->grademethod !== ['highest'=>1,'average'=>2,'first'=>3,'last'=>4][$a->grademethod] ||
            $quiz->preferredbehaviour !== 'deferredfeedback' || $quiz->intro !== $a->intro) { return false; }
    $form = new stdClass(); mcb_preparer_test($form, $a);
    quiz_process_options($form);
    foreach (['attempt','correctness','maxmarks','marks','specificfeedback','generalfeedback','rightanswer','overallfeedback'] as $k) {
        $field = 'review' . $k;
        if ((int)$quiz->$field !== (int)$form->$field) { return false; }
    }
    $bank = mcb_banque_cours($courseid, $a->bank);
    $questions = mcb_questions_banque(context_module::instance($bank->id)->id);
    $slots = array_values($DB->get_records('quiz_slots', ['quizid'=>$quiz->id], 'slot ASC'));
    if (count($slots) !== count($a->questions)) { return false; }
    foreach ($a->questions as $i=>$key) {
        $ref = $DB->get_record('question_references', ['component'=>'mod_quiz','questionarea'=>'slot','itemid'=>$slots[$i]->id], '*', MUST_EXIST);
        if (!isset($questions[$key]) || (int)$ref->questionbankentryid !== (int)$questions[$key]->questionbankentryid ||
                (int)$ref->usingcontextid !== context_module::instance($cm->id)->id || $ref->version !== null ||
                abs((float)$slots[$i]->maxmark - question_bank::load_question($questions[$key]->id)->defaultmark) > 0.000001) { return false; }
    }
    if (abs((float)$quiz->sumgrades - array_sum(array_column($slots, 'maxmark'))) > 0.000001) { return false; }
    return true;
}
