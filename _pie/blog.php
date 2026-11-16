<?php
// Mira de dónde saca el pie cada publicador diario de blog. Solo lectura.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
foreach (['classicapedia.com','worldwinepedia.com','catdogpedia.com','ludicopedia.com'] as $d) {
  $f = "/home/u235595016/domains/$d/public_html/_blog/publicar.php"; echo "== $d ", is_file($f) ? filesize($f) : 'no', "\n";
  if (!is_file($f)) continue;
  foreach (explode("\n", file_get_contents($f)) as $i => $l)
    if (preg_match('/footer|plantilla|template|file_get_contents|include|require|©|by-nc/i', $l)) echo '  ', $i + 1, ': ', mb_substr(trim($l), 0, 220), "\n";
}
