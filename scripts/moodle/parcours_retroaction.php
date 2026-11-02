<?php
// Contrat v4 : Feedback, Leçon et attestation native, uniquement dans le CLI local gardé.

function mcb_valider_parcours($s, string $projet): void {
    $previous = [];
    foreach ($s->sections as $sec) {
        foreach ($sec->activities ?? [] as $a) {
            if (!in_array($a->type ?? '', ['feedback','lesson','customcert'], true) || ($s->version ?? 1) < 4) {
                if (isset($a->idnumber)) { $previous[$a->idnumber] = $a; }
                if (($a->type ?? '') === 'lesson') { throw new InvalidArgumentException('Leçon exige le contrat v4.'); }
                continue;
            }
            if ($a->type === 'feedback') {
                if (!is_bool($a->anonymous ?? null) || !in_array($a->completion, ['none','manual','view','submit'], true) ||
                        !is_array($a->items ?? null) || !$a->items) {
                    throw new InvalidArgumentException('Feedback : anonymat, éléments et achèvement compatibles requis.');
                }
                $keys = [];
                foreach ($a->items as $item) {
                    if (!is_string($item->key ?? null) || !preg_match('/^[a-zA-Z0-9_-]+$/', $item->key) || isset($keys[$item->key]) ||
                            !in_array($item->type ?? '', ['multichoice','textfield','textarea','info','label'], true) ||
                            !is_string($item->name ?? null) || trim($item->name) === '' || !is_bool($item->required ?? false)) {
                        throw new InvalidArgumentException('Élément Feedback : clé unique, type, nom et required booléen requis.');
                    }
                    $keys[$item->key] = true;
                    if (in_array($item->type, ['info','label'], true) && ($item->required ?? false)) {
                        throw new InvalidArgumentException('Une information ne peut être une réponse obligatoire.');
                    }
                    if ($item->type === 'multichoice') {
                        if (!is_array($item->choices ?? null) || count($item->choices) < 2) { throw new InvalidArgumentException('Choix Feedback insuffisants.'); }
                        foreach ($item->choices as $choice) {
                            if (!is_string($choice) || trim($choice) === '' || preg_match('/[\r\n|]/', $choice)) {
                                throw new InvalidArgumentException('Choix Feedback : textes simples sans séparateur interne requis.');
                            }
                        }
                    } elseif ($item->type === 'label' && !is_string($item->html ?? null)) {
                        throw new InvalidArgumentException('Texte HTML de l’information requis.');
                    } elseif ($item->type === 'info' && !in_array($item->mode ?? 'course', ['course','category'], true)) {
                        throw new InvalidArgumentException('Information Feedback : cours ou catégorie seulement.');
                    }
                }
            } elseif ($a->type === 'lesson') {
                if (!in_array($a->completion, ['none','manual','view','end'], true) || !is_array($a->pages ?? null) || !$a->pages) {
                    throw new InvalidArgumentException('Leçon : pages et achèvement compatibles requis.');
                }
                $pages = [];
                foreach ($a->pages as $page) {
                    if (!is_string($page->key ?? null) || trim($page->key) === '' || $page->key === 'END' || isset($pages[$page->key]) ||
                            !in_array($page->type ?? '', ['content','question'], true) ||
                            !is_string($page->title ?? null) || trim($page->title) === '' || !is_string($page->html ?? null) ||
                            !is_array($page->choices ?? null) || count($page->choices) < ($page->type === 'question' ? 2 : 1)) {
                        throw new InvalidArgumentException('Page de Leçon : clé, type, titre, contenu et choix requis.');
                    }
                    $correct = 0;
                    foreach ($page->choices as $choice) {
                        if (!is_string($choice->text ?? null) || trim($choice->text) === '' || !is_string($choice->to ?? null) ||
                                !is_string($choice->response ?? '') || !is_bool($choice->correct ?? false)) {
                            throw new InvalidArgumentException('Choix de Leçon invalide ; destination logique requise.');
                        }
                        if ($choice->correct ?? false) { $correct++; }
                    }
                    if ($page->type === 'question' && $correct !== 1) { throw new InvalidArgumentException('Question de Leçon : un choix correct requis.'); }
                    $pages[$page->key] = $page;
                }
                // Destinations connues ; toute page doit offrir un chemin vers END, même en présence d'une boucle volontaire.
                $canend = ['END'=>true];
                foreach ($pages as $page) {
                    foreach ($page->choices as $choice) {
                        if ($choice->to !== 'END' && !isset($pages[$choice->to])) { throw new InvalidArgumentException('Saut de Leçon vers une clé absente.'); }
                    }
                }
                do {
                    $changed = false;
                    foreach ($pages as $key=>$page) {
                        foreach ($page->choices as $choice) {
                            if (!isset($canend[$key]) && isset($canend[$choice->to])) { $canend[$key] = true; $changed = true; }
                        }
                    }
                } while ($changed);
                if (count($canend) !== count($pages) + 1) { throw new InvalidArgumentException('Fin de Leçon inaccessible depuis une page.'); }
            } else {
                $c = $a->certificate ?? null;
                if (!is_object($c) || !is_string($c->background ?? null) ||
                        !isset($previous[$a->condition ?? '']) || $previous[$a->condition]->completion !== 'pass' ||
                        !in_array($a->condition_state ?? 1, [1,2], true) ||
                        !in_array($a->completion, ['none','manual','view'], true) || ($a->course_required ?? false) !== false) {
                    throw new InvalidArgumentException('Attestation : fond, condition précédente de réussite et profil sans critère de cours requis.');
                }
                $bytes = mcb_contenu($projet, $c->background);
                if (substr($bytes, 0, 8) !== "\x89PNG\r\n\x1a\n" || !getimagesizefromstring($bytes)) {
                    throw new InvalidArgumentException('Fond PNG valide requis.');
                }
                foreach (['width'=>297,'height'=>210] as $key=>$default) {
                    if (!is_int($c->$key ?? $default) || ($c->$key ?? $default) < 50 || ($c->$key ?? $default) > 1000) {
                        throw new InvalidArgumentException('Dimensions de page invalides.');
                    }
                }
            }
            $previous[$a->idnumber] = $a;
        }
    }
}

/** Représentation déterministe des éléments, hors identifiants natifs. */
function mcb_item_feedback($item, int $feedbackid, int $position): object {
    $record = (object)['id'=>0,'feedback'=>$feedbackid,'template'=>0,'name'=>$item->name,'label'=>$item->key,
        'presentation'=>'','typ'=>$item->type,'hasvalue'=>0,'position'=>$position,'required'=>(int)($item->required ?? false),
        'dependitem'=>0,'dependvalue'=>'','options'=>''];
    switch ($item->type) {
        case 'multichoice':
            $record->presentation = 'r>>>>>' . implode('|', $item->choices);
            $record->ignoreempty = 0; $record->hidenoselect = 1;
            break;
        case 'textfield': $record->presentation = '60|255'; break;
        case 'textarea': $record->presentation = '60|5'; break;
        case 'info': $record->presentation = ($item->mode ?? 'course') === 'course' ? '2' : '3'; break;
        case 'label':
            $record->presentation_editor = ['text'=>$item->html,'format'=>1,'itemid'=>0];
            $record->presentation = $item->html;
            break;
    }
    return $record;
}

function mcb_preparer_parcours($mi, $a): void {
    $mi->modulename = $a->type;
    if ($a->type === 'feedback') {
        $mi->anonymous = $a->anonymous ? 1 : 2;
        foreach (['email_notification','multiple_submit','autonumbering','publish_stats','timeopen','timeclose'] as $k) { $mi->$k = 0; }
        $mi->site_after_submit = ''; $mi->page_after_submit = '<p>Merci pour votre retour.</p>';
        $mi->page_after_submitformat = 1;
        $mi->page_after_submit_editor = ['text'=>$mi->page_after_submit,'format'=>1,'itemid'=>0];
        $mi->completionsubmit = $a->completion === 'submit' ? 1 : 0;
    } elseif ($a->type === 'lesson') {
        foreach (['ongoing','displayleft','displayleftif','slideshow','activitylink','available','deadline','usepassword',
            'dependency','timespent','completed','gradebetterthan','modattempts','review','nextpagedefault','maxpages',
            'retake','usemaxgrade','minquestions','grade','completiontimespent'] as $k) { $mi->$k = 0; }
        $mi->progressbar = 1; $mi->feedback = 1; $mi->maxattempts = 1;
        $mi->practice = 1; $mi->custom = 1; $mi->password = '';
        $mi->maxanswers = max(array_map(fn($p)=>count($p->choices), $a->pages));
        $mi->completionendreached = $a->completion === 'end' ? 1 : 0;
        $mi->mediafile = file_get_unused_draft_itemid();
    } else {
        foreach (['requiredtime','emailstudents','emailteachers','verifyany','protection_print','protection_modify','protection_copy'] as $k) { $mi->$k = 0; }
        $mi->emailothers = ''; $mi->delivery = 0;
    }
}

function mcb_finaliser_parcours($cm, $a, string $projet): void {
    global $DB, $CFG;
    if ($a->type === 'feedback') {
        require_once($CFG->dirroot . '/mod/feedback/lib.php');
        foreach ($a->items as $i=>$item) {
            $obj = feedback_get_item_class($item->type);
            $obj->set_data(mcb_item_feedback($item, $cm->instance, $i + 1));
            if (!$obj->save_item()) { throw new RuntimeException('Enregistrement d’élément Feedback refusé.'); }
        }
    } elseif ($a->type === 'lesson') {
        require_once($CFG->dirroot . '/mod/lesson/locallib.php');
        $lesson = lesson::load($cm->instance); $context = context_module::instance($cm->coursemodule);
        $pages = []; $previous = 0;
        foreach ($a->pages as $page) {
            $properties = (object)['title'=>$page->title,'qtype'=>$page->type === 'content' ? 20 : 3,
                'pageid'=>$previous,'contents_editor'=>['text'=>$page->html,'format'=>1,'itemid'=>0],
                'answer_editor'=>[],'response_editor'=>[],'jumpto'=>[],'score'=>[]];
            $created = lesson_page::create($properties, $lesson, $context, $CFG->maxbytes);
            $pages[$page->key] = $created; $previous = $created->id;
        }
        foreach ($a->pages as $page) {
            $properties = (object)['answer_editor'=>[],'response_editor'=>[],'jumpto'=>[],'score'=>[]];
            foreach ($page->choices as $i=>$choice) {
                $properties->answer_editor[$i] = $page->type === 'content' ? $choice->text : ['text'=>$choice->text,'format'=>1];
                $properties->response_editor[$i] = ['text'=>$choice->response ?? '', 'format'=>1];
                $properties->jumpto[$i] = $choice->to === 'END' ? LESSON_EOL : $pages[$choice->to]->id;
                $properties->score[$i] = ($choice->correct ?? false) ? 1 : 0;
            }
            $pages[$page->key]->create_answers($properties);
        }
    } else { mcb_finaliser_certificat($cm, $a, $projet); }
}

/** Création directe sur le schéma du plugin, sérialisation propre à chaque élément par sa fabrique. */
function mcb_finaliser_certificat($cm, $a, string $projet): void {
    global $DB, $COURSE;
    $courseid = $DB->get_field('customcert', 'course', ['id'=>$cm->instance], MUST_EXIST);
    $COURSE = get_course($courseid);
    $coursecontext = context_course::instance($courseid);
    $record = $DB->get_record('customcert', ['id'=>$cm->instance], '*', MUST_EXIST);
    $page = $DB->get_record('customcert_pages', ['templateid'=>$record->templateid], '*', MUST_EXIST);
    $page->width = $a->certificate->width ?? 297; $page->height = $a->certificate->height ?? 210;
    $page->leftmargin = 0; $page->rightmargin = 0;
    $DB->update_record('customcert_pages', $page);
    $filename = 'mcb-bg-' . substr(hash('sha256', $a->idnumber), 0, 16) . '.png';
    $fs = get_file_storage();
    if ($fs->file_exists($coursecontext->id, 'mod_customcert', 'image', 0, '/', $filename)) {
        throw new RuntimeException('Image d’attestation déjà présente dans ce contexte.');
    }
    $file = $fs->create_file_from_pathname(['contextid'=>$coursecontext->id,'component'=>'mod_customcert','filearea'=>'image',
        'itemid'=>0,'filepath'=>'/','filename'=>$filename,'userid'=>0,'author'=>'','license'=>'allrightsreserved'],
        realpath($projet . '/' . $a->certificate->background));
    foreach (['bgimage','studentname','date','code'] as $i=>$type) {
        $element = (object)['pageid'=>$page->id,'name'=>$type,'element'=>$type,'data'=>'',
            'font'=>'freesans','fontsize'=>$type === 'studentname' ? 22 : 10,'colour'=>'#182838',
            'posx'=>20,'posy'=>(int)round($page->height * [0,0.50,0.68,0.80][$i]),
            'width'=>$page->width - 40,'refpoint'=>0,'alignment'=>'C','sequence'=>$i + 1,
            'timecreated'=>time(),'timemodified'=>time()];
        $obj = \mod_customcert\element_factory::get_element_instance($element);
        if (!$obj) { throw new RuntimeException('Élément Custom certificate indisponible.'); }
        $form = (object)['fileid'=>$file->get_id(),'width'=>0,'height'=>0,'dateitem'=>'-1','dateformat'=>'strftimedate'];
        $element->data = $obj->save_unique_data($form);
        $element->id = $DB->insert_record('customcert_elements', $element);
        $obj = \mod_customcert\element_factory::get_element_instance($element);
        \mod_customcert\event\element_created::create_from_element($obj)->trigger();
    }
}

function mcb_verifier_parcours($cm, $a, string $projet): bool {
    global $DB;
    if ($a->type === 'feedback') {
        $record = $DB->get_record('feedback', ['id'=>$cm->instance], '*', MUST_EXIST);
        $items = array_values($DB->get_records('feedback_item', ['feedback'=>$cm->instance], 'position ASC'));
        if ((int)$record->anonymous !== ($a->anonymous ? 1 : 2) || (int)$record->multiple_submit !== 0 ||
                (int)$record->completionsubmit !== ($a->completion === 'submit' ? 1 : 0) || count($items) !== count($a->items)) { return false; }
        foreach ($a->items as $i=>$item) {
            $expected = mcb_item_feedback($item, $cm->instance, $i + 1);
            foreach (['name','label','typ','required','position','presentation'] as $field) {
                if ((string)$items[$i]->$field !== (string)$expected->$field) { return false; }
            }
        }
        return true;
    }
    if ($a->type === 'lesson') {
        $lesson = $DB->get_record('lesson', ['id'=>$cm->instance], '*', MUST_EXIST);
        if ((int)$lesson->completionendreached !== ($a->completion === 'end' ? 1 : 0) || (int)$lesson->grade !== 0 || (int)$lesson->practice !== 1) { return false; }
        $rows = $DB->get_records('lesson_pages', ['lessonid'=>$cm->instance]);
        if (count($rows) !== count($a->pages)) { return false; }
        $ordered = []; $id = 0;
        while (count($ordered) < count($rows)) {
            $next = array_values(array_filter($rows, fn($row)=>(int)$row->prevpageid === $id));
            if (count($next) !== 1 || isset($ordered[$next[0]->id])) { return false; }
            $ordered[$next[0]->id] = $next[0]; $id = (int)$next[0]->id;
        }
        $ordered = array_values($ordered); $ids = [];
        foreach ($a->pages as $i=>$page) { $ids[$page->key] = (int)$ordered[$i]->id; }
        foreach ($a->pages as $i=>$page) {
            $row = $ordered[$i];
            if ($row->title !== $page->title || $row->contents !== $page->html || (int)$row->qtype !== ($page->type === 'content' ? 20 : 3) ||
                    (int)$row->nextpageid !== (int)($ordered[$i + 1]->id ?? 0)) { return false; }
            $answers = array_values($DB->get_records('lesson_answers', ['pageid'=>$row->id], 'id ASC'));
            if (count($answers) !== count($page->choices)) { return false; }
            foreach ($page->choices as $j=>$choice) {
                if ($answers[$j]->answer !== $choice->text || $answers[$j]->response !== ($choice->response ?? '') ||
                        (int)$answers[$j]->jumpto !== ($choice->to === 'END' ? -9 : $ids[$choice->to]) ||
                        (int)$answers[$j]->score !== (($choice->correct ?? false) ? 1 : 0)) { return false; }
            }
        }
        return true;
    }
    $record = $DB->get_record('customcert', ['id'=>$cm->instance], '*', MUST_EXIST);
    $template = $DB->get_record('customcert_templates', ['id'=>$record->templateid], '*', MUST_EXIST);
    if ((int)$template->contextid !== context_module::instance($cm->id)->id) { return false; }
    $pages = array_values($DB->get_records('customcert_pages', ['templateid'=>$record->templateid]));
    if (count($pages) !== 1 || (int)$pages[0]->width !== ($a->certificate->width ?? 297) ||
            (int)$pages[0]->height !== ($a->certificate->height ?? 210)) { return false; }
    $elements = array_values($DB->get_records('customcert_elements', ['pageid'=>$pages[0]->id], 'sequence ASC'));
    if (array_column($elements, 'element') !== ['bgimage','studentname','date','code']) { return false; }
    foreach ($elements as $i=>$element) {
        if ((int)$element->sequence !== $i + 1 || $element->font !== 'freesans' ||
                (int)$element->fontsize !== ($i === 1 ? 22 : 10) || $element->alignment !== 'C' ||
                (int)$element->posx !== 20 || (int)$element->posy !== (int)round($pages[0]->height * [0,0.50,0.68,0.80][$i]) ||
                (int)$element->width !== (int)$pages[0]->width - 40) { return false; }
    }
    $data = json_decode($elements[0]->data);
    $context = context_course::instance($cm->course);
    if (!$data || (int)$data->contextid !== $context->id || $data->filearea !== 'image' || (int)$data->itemid !== 0 || $data->filepath !== '/') { return false; }
    $f = get_file_storage()->get_file($context->id, 'mod_customcert', 'image', 0, '/', $data->filename);
    return $f && $f->get_contenthash() === sha1_file($projet . '/' . $a->certificate->background) &&
        json_decode($elements[2]->data) == (object)['dateitem'=>'-1','dateformat'=>'strftimedate'];
}
