<?php
// Étape explicite après restauration native users=0, qui omet les entrées du Glossaire.
// Reprend uniquement les définitions du modèle transportées dans sa zone intro.
define('CLI_SCRIPT',true);
$opts = getopt('', ['moodle:','courseid:','validation-locale']);
if (!isset($opts['validation-locale']) || empty($opts['moodle']) ||
        !ctype_digit((string)($opts['courseid'] ?? '')) || (int)$opts['courseid'] < 1) {
    fwrite(STDERR,"Exiger --validation-locale --moodle --courseid positif.\n"); exit(2);
}
require(rtrim($opts['moodle'],'/\\') . '/config.php');
require(__DIR__ . '/validation_locale.php');
require_once($CFG->dirroot . '/mod/glossary/lib.php');
require_once(__DIR__ . '/activites_etendues.php');
$course = get_course((int)$opts['courseid']);
if ((int)$course->visible !== 0) { fwrite(STDERR,"Cours local masqué requis.\n"); exit(2); }
$pending = [];
// Tout précontrôler avant d'ajouter une entrée : ne jamais écraser un lexique existant.
foreach (get_fast_modinfo($course)->cms as $cm) {
    if ($cm->modname !== 'glossary') { continue; }
    $ctx = context_module::instance($cm->id);
    $file = get_file_storage()->get_file($ctx->id,'mod_glossary','intro',0,'/','entrees-modele.json');
    if (!$file) { continue; }
    $entries = json_decode($file->get_content(),false,512,JSON_THROW_ON_ERROR);
    if (!is_array($entries) || !$entries) { throw new RuntimeException('Définitions transportées invalides.'); }
    $concepts = [];
    foreach ($entries as $e) {
        if (!is_string($e->concept ?? null) || trim($e->concept) === '' ||
                !is_string($e->definition ?? null) || isset($concepts[$e->concept])) {
            throw new RuntimeException('Définition ou concept invalide.');
        }
        $concepts[$e->concept] = $e->definition;
    }
    $existing = $DB->get_records('glossary_entries',['glossaryid'=>$cm->instance]);
    if ($existing) {
        $actual = [];
        foreach ($existing as $e) { $actual[$e->concept] = $e->definition; }
        ksort($actual); ksort($concepts);
        if ($actual !== $concepts || count($existing) !== count($concepts)) {
            throw new RuntimeException('Glossaire non vide et différent : aucune entrée écrasée.');
        }
        continue;
    }
    $pending[] = [$cm,$entries];
}
\core\session\manager::set_user(get_admin());
foreach ($pending as [$cm,$entries]) {
    $glossary = $DB->get_record('glossary',['id'=>$cm->instance],'*',MUST_EXIST);
    foreach ($entries as $entry) {
        glossary_edit_entry((object)['concept'=>$entry->concept,'aliases'=>'',
            'definition_editor'=>['text'=>$entry->definition,'format'=>FORMAT_HTML,'itemid'=>file_get_unused_draft_itemid()]],
            $course,$cm,$glossary,context_module::instance($cm->id));
    }
}
echo count($pending) . " Glossaire(s) complété(s) par les définitions du modèle ; aucun utilisateur source repris.\n";
