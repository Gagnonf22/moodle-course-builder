<?php
// Garde des actions après config.php ; ne prouve pas l’isolation du bootstrap.
// Contrôle complémentaire : le site déclaré doit être sur la boucle locale.
$hote = parse_url($CFG->wwwroot, PHP_URL_HOST);
if (!in_array($hote, ['localhost', '127.0.0.1', '[::1]', '::1'], true)) {
    fwrite(STDERR, "Instance refusée : wwwroot doit désigner la boucle locale.\n");
    exit(2);
}

// config.php est déjà chargé : garde des actions ci-dessous, pas du bootstrap.
// Moodle demande dbhost=localhost même avec dboptions['dbsocket'].
$dbhost = $CFG->dbhost ?? null;
if (!is_string($dbhost) || !in_array($dbhost, ['localhost', '127.0.0.1', '::1', '[::1]'], true)) {
    fwrite(STDERR, "Base refusée : dbhost doit être explicitement local (localhost, 127.0.0.1 ou ::1).\n");
    exit(2);
}
$socket = $CFG->dboptions['dbsocket'] ?? false;
if ($socket !== false && $socket !== true && $socket !== '' && $socket !== null &&
        (!is_string($socket) || !str_starts_with($socket, '/') || str_starts_with($socket, '//') ||
         str_contains($socket, '\\') || str_contains($socket, "\0"))) {
    fwrite(STDERR, "Base refusée : socket Unix local absolu attendu.\n");
    exit(2);
}
if ($socket && $dbhost !== 'localhost') {
    fwrite(STDERR, "Base refusée : un socket exige dbhost=localhost.\n");
    exit(2);
}

