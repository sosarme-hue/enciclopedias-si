<?php
// Busca dónde se genera el pie de las guías WordPress .si. Solo lectura.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
foreach (['sitges','santperederibes','castelldefels','santcugat','vilanova','garraf','eivissa'] as $d) {
  $p = "/home/u235595016/domains/$d.si/public_html/wp-content";
  echo "== $d.si\n";
  foreach (array_merge(glob("$p/themes/*", GLOB_ONLYDIR) ?: [], glob("$p/plugins/*", GLOB_ONLYDIR) ?: [], ["$p/mu-plugins"]) as $dir) {
    if (!is_dir($dir)) continue;
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir, FilesystemIterator::SKIP_DOTS));
    $n = 0;
    foreach ($it as $f) {
      if (++$n > 4000) break;
      if (!preg_match('/\.php$/', $f->getFilename())) continue;
      $c = @file_get_contents($f->getPathname()); if ($c === false) continue;
      if (strpos($c, 'Datos del directorio') === false && strpos($c, 'ssi-footer__credit') === false) continue;
      foreach (explode("\n", $c) as $i => $l) if (strpos($l, 'Datos del directorio') !== false || strpos($l, 'ssi-footer__credit') !== false || strpos($l, 'Data from') !== false)
        echo substr($f->getPathname(), strlen($p) + 1), ':', $i + 1, ': ', mb_substr(trim($l), 0, 330), "\n";
    }
  }
}
