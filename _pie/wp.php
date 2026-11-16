<?php
// Instala o quita el mu-plugin del pie de licencia en las guías WordPress .si.
// Uso (solo por línea de órdenes): php wp.php instalar|quitar [dominio,dominio]
// Al instalar, abre la portada (sin caché) y, si la página falla o no muestra la línea, quita el archivo al momento.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
$modo = $argv[1] ?? 'comprobar';
$WP = ['sitges.si','santperederibes.si','castelldefels.si','santcugat.si','vilanova.si','garraf.si','eivissa.si'];
$doms = array_values(array_intersect($WP, array_filter(explode(',', $argv[2] ?? '')))) ?: $WP;
$src = __DIR__ . '/wp/pie-licencia.php';
$ctx = stream_context_create(['http' => ['timeout' => 30, 'ignore_errors' => true, 'user_agent' => 'Mozilla/5.0 (pie)']]);
$ver = function ($d) use ($ctx) {
  $h = @file_get_contents("https://$d/?pie=" . time() . mt_rand(), false, $ctx);
  $st = isset($http_response_header[0]) ? $http_response_header[0] : '?';
  return [$st, (string)$h];
};
foreach ($doms as $d) {
  $dst = "/home/u235595016/domains/$d/public_html/wp-content/mu-plugins/pie-licencia.php";
  if ($modo === 'quitar') { echo "$d: ", (is_file($dst) && unlink($dst)) ? "quitado" : "no estaba", "\n"; continue; }
  if ($modo === 'instalar') {
    if (!is_file($dst)) { @mkdir(dirname($dst), 0755, true); if (!copy($src, $dst)) { echo "$d: no se pudo copiar\n"; continue; } }
    [$st, $h] = $ver($d);
    $ok = strpos($st, ' 200') !== false && strlen($h) > 20000 && strpos($h, 'creativecommons.org/licenses/by-nc/4.0') !== false && stripos($h, '</html>') !== false;
    if (!$ok) { unlink($dst); echo "$d: FALLO ($st, " . strlen($h) . " bytes) -> quitado\n"; continue; }
    preg_match('~<span>© 2026 Alejandro Rosàs[^\n]{0,330}~u', $h, $m);
    echo "$d: ok ($st) ", $m[0] ?? '', "\n";
    continue;
  }
  [$st, $h] = $ver($d);
  echo "$d: ", is_file($dst) ? 'instalado' : 'no instalado', " | $st | ", strpos($h, 'by-nc/4.0') !== false ? 'con línea' : 'sin línea', "\n";
}
