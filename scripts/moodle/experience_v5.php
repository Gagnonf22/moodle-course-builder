<?php
// Contrat v5 : ressources pédagogiques et séparation remise/réussite.

function mcb_conditions($a): array {
    return $a->conditions ?? [(object)['type'=>'completion', 'activity'=>$a->condition,
        'state'=>$a->condition_state ?? 1]];
}

/** Valide les dépendances avant création, sans résoudre d'identifiant d'un autre cours. */
function mcb_valider_conditions($a, array $previous): bool {
    if (!is_array($a->conditions) || !$a->conditions || isset($a->condition) || isset($a->condition_state)) {
        throw new InvalidArgumentException('Attestation : conditions non vides, sans ancienne condition simultanée.');
    }
    $seen = [];
    foreach ($a->conditions as $c) {
        $target = $previous[$c->activity ?? ''] ?? null;
        $key = ($c->type ?? '') . ':' . ($c->activity ?? '');
        if (!$target || isset($seen[$key]) || !in_array($c->type ?? '', ['completion','grade'], true)) {
            throw new InvalidArgumentException('Condition absente, future, dupliquée ou inconnue.');
        }
        $seen[$key] = true;
        if ($c->type === 'completion') {
            if (!in_array($c->state ?? 1, [1,2], true) || $target->completion === 'none' ||
                    (($c->state ?? 1) === 2 && $target->completion !== 'pass')) {
                throw new InvalidArgumentException('Condition : achèvement actif et état compatible requis.');
            }
        } elseif (!in_array($target->type, ['quiz','h5p','assign'], true) ||
                ($target->type === 'assign' && ($target->grade ?? 0) <= 0) ||
                !mcb_nombre($c->min ?? null) || $c->min < 0 || $c->min > 100) {
            throw new InvalidArgumentException('Condition de note : activité notée et minimum sur 100 requis.');
        }
    }
    return true;
}

function mcb_availability_certificat($a, int $courseid): object {
    global $DB;
    $conditions = [];
    foreach (mcb_conditions($a) as $c) {
        $cm = $DB->get_record('course_modules', ['course'=>$courseid,'idnumber'=>$c->activity], '*', MUST_EXIST);
        if ($c->type === 'completion') {
            $conditions[] = (object)['type'=>'completion','cm'=>(int)$cm->id,'e'=>$c->state ?? 1];
        } else {
            $module = $DB->get_field('modules','name',['id'=>$cm->module],MUST_EXIST);
            $gi = grade_item::fetch(['courseid'=>$courseid,'itemmodule'=>$module,'iteminstance'=>$cm->instance]);
            if (!$gi) { throw new RuntimeException('Élément de note de la condition absent.'); }
            $conditions[] = (object)['type'=>'grade','id'=>(int)$gi->id,'min'=>(float)$c->min];
        }
    }
    return (object)['op'=>'&','c'=>$conditions,'showc'=>array_fill(0,count($conditions),true)];
}

function mcb_h5p_integre($a, int $version): bool {
    return $a->type === 'h5p' && $version >= 5 && ($a->embed ?? ($a->completion !== 'pass'));
}

function mcb_valider_v5($s, string $projet): void {
    $version = $s->version ?? 1;
    foreach ($s->sections as $sec) {
        if ($version >= 5) { mcb_contenu($projet, $sec->summary); }
        $embedded = [];
        foreach ($sec->activities ?? [] as $a) {
            if ($version < 5 && ($a->type === 'glossary' || isset($a->conditions) ||
                    isset($a->attachments) || isset($a->embed))) {
                throw new InvalidArgumentException('Glossaire et nouveaux champs exigent le contrat v5.');
            }
            if ($version < 5) { continue; }
            if (isset($a->conditions) && $a->type !== 'customcert') {
                throw new InvalidArgumentException('conditions est réservé à l’attestation.');
            }
            if (isset($a->embed) && ($a->type !== 'h5p' || !is_bool($a->embed))) {
                throw new InvalidArgumentException('embed exige un H5P et un booléen.');
            }
            if (mcb_h5p_integre($a,$version)) { $embedded[$a->idnumber] = true; }
            if (isset($a->attachments)) {
                if ($a->type !== 'assign' || !is_array($a->attachments)) {
                    throw new InvalidArgumentException('attachments : liste de fichiers du Devoir requise.');
                }
                $names = [];
                foreach ($a->attachments as $file) {
                    if (!is_string($file)) { throw new InvalidArgumentException('Chemin de pièce joint requis.'); }
                    mcb_contenu($projet,$file);
                    $name = strtolower(basename(str_replace('\\','/',$file)));
                    if (isset($names[$name])) { throw new InvalidArgumentException('Pièces jointes de même nom.'); }
                    $names[$name] = true;
                }
            }
            if ($a->type === 'glossary') {
                if (!in_array($a->completion,['none','manual','view'],true) ||
                        !is_array($a->entries ?? null) || !$a->entries) {
                    throw new InvalidArgumentException('Glossaire : entrées et mode de consultation requis.');
                }
                $concepts = [];
                foreach ($a->entries as $entry) {
                    if (!is_string($entry->concept ?? null) || trim($entry->concept) === '' ||
                            trim($entry->concept) !== $entry->concept ||
                            !is_string($entry->definition ?? null) || trim($entry->definition) === '' ||
                            isset($concepts[$entry->concept])) {
                        throw new InvalidArgumentException('Glossaire : concepts uniques et définitions non vides requis.');
                    }
                    $concepts[$entry->concept] = true;
                }
            }
        }
        if ($version >= 5) {
            preg_match_all('/\{\{h5p:([^}]+)\}\}/',mcb_contenu($projet,$sec->summary),$matches);
            $seen = [];
            foreach ($matches[1] as $key) {
                if (!isset($embedded[$key]) || isset($seen[$key])) {
                    throw new InvalidArgumentException('Marqueur H5P inconnu, non intégré ou répété dans la section.');
                }
                $seen[$key] = true;
            }
        }
    }
}

/** HTML attendu, également recalculé après restauration avec les nouveaux contextes. */
function mcb_resume_section($sec, string $projet, int $courseid, int $version): string {
    global $CFG, $DB;
    $html = mcb_contenu($projet,$sec->summary);
    foreach ($sec->activities as $a) {
        if (!mcb_h5p_integre($a,$version)) { continue; }
        $cmid = $DB->get_field('course_modules','id',['course'=>$courseid,'idnumber'=>$a->idnumber],MUST_EXIST);
        $ctx = context_module::instance($cmid);
        $url = $CFG->wwwroot . '/pluginfile.php/' . $ctx->id . '/mod_h5pactivity/package/0/' .
            rawurlencode(basename($a->package)) . '?component=mod_h5pactivity';
        $marker = '<div class="h5p-placeholder">' . htmlspecialchars($url,ENT_QUOTES,'UTF-8') . '</div>';
        $token = '{{h5p:' . $a->idnumber . '}}';
        $html = str_contains($html,$token) ? str_replace($token,$marker,$html) : $html . "\n" . $marker;
    }
    return $html;
}

function mcb_preparer_glossaire($mi): void {
    $mi->modulename = 'glossary';
    foreach (['globalglossary','mainglossary','allowcomments','allowduplicatedentries','usedynalink',
            'assessed','scale','editalways','completionentries'] as $key) { $mi->$key = 0; }
    $mi->defaultapproval = 1;
    $mi->displayformat = 'dictionary';
    $mi->entbypage = 10;
    $mi->showalphabet = 1; $mi->showall = 1; $mi->showspecial = 1;
}

function mcb_termes_modele(array $entries): array {
    return array_map(fn($e)=>(object)['concept'=>$e->concept,'definition'=>$e->definition],$entries);
}

function mcb_finaliser_glossaire($cm, $a): void {
    global $CFG, $DB;
    require_once($CFG->dirroot . '/mod/glossary/lib.php');
    $glossary = $DB->get_record('glossary',['id'=>$cm->instance],'*',MUST_EXIST);
    foreach ($a->entries as $entry) {
        glossary_edit_entry((object)['concept'=>$entry->concept,'aliases'=>'',
            'definition_editor'=>['text'=>$entry->definition,'format'=>FORMAT_HTML,'itemid'=>file_get_unused_draft_itemid()]],
            get_course($cm->course), $cm, $glossary, context_module::instance($cm->coursemodule));
    }
    // Moodle omet les entrées lors d'une sauvegarde users=0. Les définitions du modèle,
    // sans auteur ni données d'usage, voyagent donc aussi dans la zone intro sauvegardée.
    get_file_storage()->create_file_from_string(['contextid'=>context_module::instance($cm->coursemodule)->id,
        'component'=>'mod_glossary','filearea'=>'intro','itemid'=>0,'filepath'=>'/',
        'filename'=>'entrees-modele.json'], json_encode(mcb_termes_modele($a->entries),JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR));
}

function mcb_verifier_glossaire($cm, $a): bool {
    global $DB;
    $record = $DB->get_record('glossary',['id'=>$cm->instance],'*',MUST_EXIST);
    $entries = array_values($DB->get_records('glossary_entries',['glossaryid'=>$cm->instance],'id ASC'));
    if ($record->displayformat !== 'dictionary' || (int)$record->assessed !== 0 || count($entries) !== count($a->entries)) { return false; }
    $expected = [];
    foreach ($a->entries as $e) { $expected[$e->concept] = $e->definition; }
    foreach ($entries as $e) {
        if (!isset($expected[$e->concept]) || $expected[$e->concept] !== $e->definition ||
                (int)$e->definitionformat !== (int)FORMAT_HTML || (int)$e->approved !== 1) { return false; }
        unset($expected[$e->concept]);
    }
    $portable = get_file_storage()->get_file(context_module::instance($cm->id)->id,'mod_glossary','intro',0,'/','entrees-modele.json');
    return !$expected && $portable && json_decode($portable->get_content()) == mcb_termes_modele($a->entries);
}

function mcb_verifier_pieces($cm, $a, string $projet): bool {
    $files = get_file_storage()->get_area_files(context_module::instance($cm->id)->id,'mod_assign','introattachment',0,'',false);
    $expected = [];
    foreach ($a->attachments ?? [] as $path) { $expected[basename($path)] = sha1(mcb_contenu($projet,$path)); }
    if (count($files) !== count($expected)) { return false; }
    foreach ($files as $f) {
        if (($expected[$f->get_filename()] ?? null) !== $f->get_contenthash()) { return false; }
    }
    return true;
}

/** Probes v5 : l'état d'accès attendu est indépendant de l'achèvement du Test. */
function mcb_verifier_acces_v5($cm, $course, $probes): void {
    foreach ($probes->cases ?? [] as $case) {
        $uid = $case->userid ?? 0;
        if (!is_int($uid) || $uid < 1 || !is_bool($case->allowed ?? null) ||
                !is_enrolled(context_course::instance($course->id),$uid,'',true) || is_siteadmin($uid) ||
                has_capability('moodle/course:manageactivities',context_course::instance($course->id),$uid) ||
                has_capability('moodle/course:ignoreavailabilityrestrictions',context_module::instance($cm->id),$uid)) {
            verif(false,'attestation : compte apprenant et attente explicite requis'); continue;
        }
        $mi = get_fast_modinfo($course,$uid);
        $info = new \core_availability\info_module($mi->get_cm($cm->id));
        $why = '';
        verif($info->is_available($why,false,$uid) === $case->allowed,'attestation : accès réel du cas d’essai');
    }
    if (empty($probes->cases)) { echo "  INFO  Accès apprenant v5 : À valider séparément (--apprenants avec cases).\n"; }
}
