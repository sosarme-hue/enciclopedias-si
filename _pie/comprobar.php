<?php
// Comprueba el pie nuevo en las webs: para cada una, unos ejemplos con el texto alrededor de la línea y si sale repetida. Solo lectura.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
foreach (glob(__DIR__ . '/apl-*.json') as $j) {
  $d = substr(basename($j, '.json'), 4); $a = json_decode(file_get_contents($j), true);
  $raiz = "/home/u235595016/domains/$d/public_html";
  $ej = $a['ultimo']['ejemplos'] ?? []; $ej = array_slice(array_merge(['index.html', 'en/index.html'], $ej), 0, 4);
  echo "== $d: cambiados {$a['cambiados']}, ", isset($a['terminado']) ? 'terminado' : 'en curso', ", sin pie " . ($a['terminado']['sin_pie'] ?? '-') . "\n";
  foreach ($ej as $e) { $f = "$raiz/$e"; if (!is_file($f)) continue; $s = file_get_contents($f);
    $n = substr_count($s, 'by-nc/4.0'); $i = strpos($s, 'by-nc/4.0');
    echo "  $e x$n: ", $i === false ? '-' : preg_replace('/\s+/', ' ', substr($s, max(0, $i - 190), 330)), "\n"; }
}
