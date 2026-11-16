<?php
// Pie de autoría y licencia (CC BY-NC 4.0) para las webs estáticas de Alex.
// Uso (solo por línea de órdenes): php pie.php inventario|aplicar|restaurar DOMINIO[,DOMINIO...]
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
@set_time_limit(0); ini_set('memory_limit', '1024M');
$HOME = getenv('PIE_HOME') ?: '/home/u235595016';
$AQUI = __DIR__;
$COPIAS = "$HOME/copias-pie";
$modo = $argv[1] ?? 'inventario';
$doms = array_filter(explode(',', $argv[2] ?? ''));
$URL = 'https://creativecommons.org/licenses/by-nc/4.0/deed.';
$TXT = [
 'es' => ['Contenido bajo licencia', 'salvo indicación en contrario'],
 'ca' => ['Contingut sota llicència', "llevat que s'indiqui el contrari"],
 'en' => ['Content licensed under', 'unless otherwise noted'],
 'fr' => ['Contenu sous licence', 'sauf mention contraire'],
 'it' => ['Contenuti con licenza', 'salvo diversa indicazione'],
 'de' => ['Inhalt lizenziert unter', 'sofern nicht anders angegeben'],
 'pt' => ['Conteúdo sob licença', 'salvo indicação em contrário'],
];
function linea($l) { global $TXT, $URL; [$a, $b] = $TXT[$l] ?? $TXT['es']; $l = isset($TXT[$l]) ? $l : 'es';
  return "© 2026 Alejandro Rosàs · $a <a href=\"$URL$l\" rel=\"license noopener\" style=\"display:inline\">CC BY-NC 4.0</a>, $b"; }
function idioma($s) { if (preg_match('/<html[^>]*\blang="([a-zA-Z]{2})/i', $s, $m)) return strtolower($m[1]); return 'es'; }
function ficheros($raiz) {
  $out = [];
  $it = new RecursiveIteratorIterator(new RecursiveCallbackFilterIterator(
    new RecursiveDirectoryIterator($raiz, FilesystemIterator::SKIP_DOTS),
    function ($f, $k, $it) use ($raiz) {
      if ($f->isLink()) return false;
      if ($f->isDir()) { $n = $f->getFilename();
        if ($n === '.git' || $n === 'node_modules' || $n === 'wp-content' || $n === 'wp-includes' || $n === 'wp-admin') return false;
        if (file_exists($f->getPathname() . '/.git')) return false; // subcarpeta con su propio repositorio
        return true; }
      return preg_match('/\.(html?|php)$/i', $f->getFilename());
    }));
  foreach ($it as $f) $out[] = $f->getPathname();
  return $out;
}
function norm($s) { $s = preg_replace('/href="[^"]*"/', 'href', $s); $s = preg_replace('/\s+/', ' ', $s); return trim($s); }
$log = [];
foreach ($doms as $d) {
  $raiz = "$HOME/domains/$d/public_html";
  if (!is_dir($raiz)) { $log[$d] = 'no existe'; continue; }
  $fs = ficheros($raiz);
  if ($modo === 'inventario') {
    $r = ['ficheros' => count($fs), 'git_raiz' => file_exists("$raiz/.git"), 'idiomas' => [], 'con_footer' => 0, 'ya_cc' => 0, 'copyright' => [], 'final_footer' => [], 'sin_footer_ejemplos' => [], 'dirs' => []];
    foreach ($fs as $f) {
      $s = @file_get_contents($f); if ($s === false) continue;
      $rel = substr($f, strlen($raiz) + 1);
      $top = explode('/', $rel)[0]; $r['dirs'][$top] = ($r['dirs'][$top] ?? 0) + 1;
      if (strpos($s, 'creativecommons.org/licenses/by-nc/4.0') !== false) $r['ya_cc']++;
      $l = idioma($s); $r['idiomas'][$l] = ($r['idiomas'][$l] ?? 0) + 1;
      $i = strripos($s, '</footer>');
      if ($i !== false) { $r['con_footer']++; $k = norm(substr($s, max(0, $i - 260), 260)); $r['final_footer'][$k] = ($r['final_footer'][$k] ?? 0) + 1; }
      elseif (count($r['sin_footer_ejemplos']) < 8) $r['sin_footer_ejemplos'][] = $rel;
      if (preg_match_all('/.{0,90}(?:©|&copy;|&#169;).{0,90}/u', $s, $m)) foreach ($m[0] as $x) { $k = norm(preg_replace('/\d{4}/', 'AAAA', $x)); $r['copyright'][$k] = ($r['copyright'][$k] ?? 0) + 1; }
    }
    arsort($r['final_footer']); $r['final_footer'] = array_slice($r['final_footer'], 0, 6, true);
    arsort($r['copyright']); $r['copyright'] = array_slice($r['copyright'], 0, 8, true);
    arsort($r['dirs']); $r['dirs'] = array_slice($r['dirs'], 0, 15, true);
    $log[$d] = $r;
  }
}
$f = "$AQUI/informe-$modo.json";
file_put_contents($f, json_encode($log, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
echo "ok $modo " . implode(',', $doms) . "\n";
