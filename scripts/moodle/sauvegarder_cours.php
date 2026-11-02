<?php
// Export natif sans données d'utilisateurs ; instance locale jetable uniquement.
define('CLI_SCRIPT', true);
$opts = getopt('', ['moodle:', 'courseid:', 'fichier:', 'validation-locale']);
if (!isset($opts['validation-locale']) || empty($opts['moodle']) ||
        !ctype_digit((string)($opts['courseid'] ?? '')) || (int)$opts['courseid'] < 1 || empty($opts['fichier'])) {
    fwrite(STDERR, "Exiger --validation-locale --moodle --courseid positif --fichier nouveau.mbz.\n");
    exit(2);
}
$output = $opts['fichier'];
if (strtolower(pathinfo($output, PATHINFO_EXTENSION)) !== 'mbz' || file_exists($output) || is_link($output)) {
    fwrite(STDERR, "Sortie .mbz neuve requise.\n");
    exit(2);
}
require(rtrim($opts['moodle'], '/\\') . '/config.php');
require(__DIR__ . '/validation_locale.php');
require_once($CFG->dirroot . '/backup/util/includes/backup_includes.php');
$bc = null;
$stream = null;
$reserved = false;
try {
    $course = get_course((int)$opts['courseid']);
    if ((int)$course->visible !== 0) {
        throw new RuntimeException('Seul un cours masqué de validation peut être exporté par ce script.');
    }
    $stream = @fopen($output, 'xb');
    if (!$stream) { throw new RuntimeException('Impossible de réserver une sortie neuve.'); }
    $reserved = true;
    $admin = get_admin();
    \core\session\manager::set_user($admin);
    $bc = new backup_controller(backup::TYPE_1COURSE, $course->id, backup::FORMAT_MOODLE,
        backup::INTERACTIVE_NO, backup::MODE_GENERAL, $admin->id);
    $plan = $bc->get_plan();
    // users est obligatoire ; ne jamais continuer si une exclusion verrouillée reste active.
    $exclus = ['users', 'anonymize', 'role_assignments', 'comments', 'badges', 'calendarevents',
        'userscompletion', 'logs', 'grade_histories', 'groups', 'competencies', 'xapistate', 'legacyfiles'];
    if (!$plan->setting_exists('users')) { throw new RuntimeException('Réglage users absent.'); }
    foreach ($exclus as $name) {
        if (!$plan->setting_exists($name)) { continue; }
        $setting = $plan->get_setting($name);
        if ($setting->get_status() == base_setting::NOT_LOCKED) { $setting->set_value(0); }
        if ((int)$setting->get_value() !== 0) { throw new RuntimeException("Exclusion refusée : $name"); }
    }
    // Inclure les fichiers et la banque de contenus, indépendamment des défauts du site.
    foreach (['activities', 'blocks', 'filters', 'files', 'contentbankcontent'] as $name) {
        $setting = $plan->get_setting($name);
        if ($setting->get_status() == base_setting::NOT_LOCKED) { $setting->set_value(1); }
        if ((int)$setting->get_value() !== 1) { throw new RuntimeException("Contenu désactivé : $name"); }
    }
    $plan->get_setting('filename')->set_value(basename($output));
    // Recontrôler users après propagation des dépendances de réglages.
    if ((int)$plan->get_setting('users')->get_value() !== 0) { throw new RuntimeException('users réactivé.'); }
    $bc->execute_plan();
    $file = $bc->get_results()['backup_destination'] ?? null;
    if (!$file) { throw new RuntimeException('Résultat natif absent.'); }
    $input = $file->get_content_file_handle();
    try {
        $copied = stream_copy_to_stream($input, $stream);
    } finally {
        if (is_resource($input)) { fclose($input); }
    }
    if ($copied !== (int)$file->get_filesize() || $copied < 1 || !fflush($stream)) {
        throw new RuntimeException('Copie de sauvegarde incomplète.');
    }
    fclose($stream);
    $stream = null;
    $bc->destroy();
    $bc = null;
    echo "Sauvegarde locale produite, users=0. Inspecter le .mbz et tester sa restauration.\n";
} catch (Throwable $e) {
    if (is_resource($stream)) { fclose($stream); }
    if ($reserved) { @unlink($output); }
    fwrite(STDERR, "Sauvegarde refusée ou échouée : " . $e->getMessage() . "\n");
    exit(2);
} finally {
    if ($bc !== null) { $bc->destroy(); }
}
