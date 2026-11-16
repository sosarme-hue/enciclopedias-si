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
$TODAS = ['mythicapedia.com','iapedia.si','celebraciones.org','catdogpedia.com','ludicopedia.com','zodiacopedia.com','culinapedia.com','newtonpedia.com','cinematopedia.com','pinacopedia.com','filopedia.com','tenispedia.com','clasicapedia.com','classicalarchive.org','medicapedia.org','classicapedia.com'];
if ($doms === ['todas']) $doms = $TODAS;
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
function guardar($aqui, $modo, $d, $r) { file_put_contents("$aqui/inv-$d.json", json_encode($r, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)); }
function norm($s) { $s = preg_replace('/href="[^"]*"/', 'href', $s); $s = preg_replace('/\s+/', ' ', $s); return trim($s); }
$REGLAS = is_file("$AQUI/reglas.php") ? include "$AQUI/reglas.php" : [];
$lockg = fopen("$AQUI/pie.lock", 'c'); if (!flock($lockg, LOCK_EX | LOCK_NB)) { echo "ocupado\n"; exit; }
$log = [];

if ($modo === 'wpinfo') {
  $WP = ['sitges.si','santperederibes.si','castelldefels.si','santcugat.si','vilanova.si','garraf.si','eivissa.si'];
  if ($doms === ['todas'] || !$doms) $doms = $WP;
  foreach ($doms as $d) {
    $p = "$HOME/domains/$d/public_html";
    $wp = function ($args) use ($p) { $o = []; exec('wp --path=' . escapeshellarg($p) . ' --skip-plugins --skip-themes ' . $args . ' 2>&1', $o); return implode("\n", $o); };
    $r = [];
    $r['tema'] = $wp('theme list --status=active --fields=name,version,template --format=json');
    $r['hijo_padre'] = $wp('option get template') . ' / ' . $wp('option get stylesheet');
    $mods = json_decode($wp('theme mod list --format=json'), true) ?: [];
    $r['mods'] = [];
    foreach ($mods as $m) { $k = $m['key'] ?? ''; $v = is_string($m['value'] ?? null) ? $m['value'] : json_encode($m['value'] ?? null, JSON_UNESCAPED_UNICODE);
      if (preg_match('/foot|copy|credit|pie/i', $k) || preg_match('/©|&copy;/u', (string)$v)) $r['mods'][$k] = mb_substr((string)$v, 0, 400); }
    $r['plugins_activos'] = $wp('plugin list --status=active --field=name');
    $r['widgets_pie'] = mb_substr($wp('widget list footer-1 --format=json') . ' | ' . $wp('sidebar list --fields=id,name --format=json'), 0, 1500);
    $t = trim($wp('option get stylesheet'));
    foreach (glob("$p/wp-content/themes/$t/*.php") ?: [] as $f) { $c = file_get_contents($f); if (preg_match_all('/.{0,120}(©|&copy;|copyright).{0,160}/iu', $c, $m)) $r['tema_copy'][basename($f)] = array_slice($m[0], 0, 4); }
    $r['opciones_copy'] = mb_substr($wp("db query \"SELECT option_name, LEFT(option_value,300) FROM " . trim($wp('db prefix')) . "options WHERE option_value LIKE '%©%' OR option_value LIKE '%&copy;%' LIMIT 20\" --skip-column-names"), 0, 4000);
    $log[$d] = $r;
    guardar($AQUI, 'wp', $d, $r);
  }
}

if ($modo !== 'wpinfo')
foreach ($doms as $d) {
  $raiz = "$HOME/domains/$d/public_html";
  if (!is_dir($raiz)) { $log[$d] = 'no existe'; continue; }
  $fs = ficheros($raiz);
  if ($modo === 'inventario') {
    if (is_file("$AQUI/inv-$d.json")) continue;
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
    guardar($AQUI, $modo, $d, $r);
  }
  if ($modo === 'aplicar') {
    $cfg = $REGLAS[$d] ?? null; if (!$cfg) { $log[$d] = 'sin reglas'; continue; }
    $cambios = []; $omitidos = 0; $ya = 0;
    foreach ($fs as $f) {
      $s = @file_get_contents($f); if ($s === false) continue;
      if (strpos($s, 'creativecommons.org/licenses/by-nc/4.0') !== false) { $ya++; continue; }
      $L = linea(idioma($s)); $n = 0;
      if (!empty($cfg['sustituir']) && preg_match($cfg['sustituir'], $s)) {
        $nuevo = preg_replace_callback($cfg['sustituir'], function ($m) use ($L, $cfg) { return strtr($cfg['por'], ['LINEA' => $L, '$1' => $m[1] ?? '', '$2' => $m[2] ?? '']); }, $s, 1);
      } elseif (!empty($cfg['insertar'])) {
        $i = strripos($s, $cfg['insertar']); if ($i === false) { $omitidos++; continue; }
        $nuevo = substr($s, 0, $i) . str_replace('LINEA', $L, $cfg['html']) . substr($s, $i);
      } else { $omitidos++; continue; }
      if ($nuevo === null || $nuevo === $s) { $omitidos++; continue; }
      $cambios[$f] = $nuevo;
    }
    $rel = []; $raizlen = strlen($raiz) + 1; foreach (array_keys($cambios) as $f) $rel[] = substr($f, $raizlen);
    $n = count($cambios);
    if ($n) {
      @mkdir($COPIAS, 0700, true);
      $copia = "$COPIAS/$d-" . date('Ymd-His') . '.tar';
      $lista = tempnam(sys_get_temp_dir(), 'pie'); file_put_contents($lista, implode("\n", $rel) . "\n");
      exec('tar -C ' . escapeshellarg($raiz) . ' -cf ' . escapeshellarg($copia) . ' -T ' . escapeshellarg($lista) . ' 2>&1', $o, $rc);
      unlink($lista);
      if ($rc !== 0 || !is_file($copia)) { $log[$d] = ['error' => 'no se pudo hacer la copia', 'tar' => $o]; continue; }
      exec('tar -tf ' . escapeshellarg($copia) . ' 2>/dev/null', $dentro);
      if (count($dentro) < $n) { $log[$d] = ['error' => 'copia incompleta', 'en_copia' => count($dentro), 'a_cambiar' => $n]; continue; }
      exec('gzip -f ' . escapeshellarg($copia)); if (is_file("$copia.gz")) $copia .= '.gz';
      $esc = 0; foreach ($cambios as $f => $c) { $t = "$f.pie-tmp"; if (file_put_contents($t, $c) !== false && rename($t, $f)) $esc++; }
      $log[$d] = ['cambiados' => $esc, 'ya_tenian' => $ya, 'sin_pie' => $omitidos, 'copia' => $copia, 'ejemplos' => array_slice($rel, 0, 5)];
    } else $log[$d] = ['cambiados' => 0, 'ya_tenian' => $ya, 'sin_pie' => $omitidos];
  }
  if ($modo === 'restaurar') {
    $cs = glob("$COPIAS/$d-*.tar*"); sort($cs); $c = end($cs);
    if (!$c) { $log[$d] = 'sin copia'; continue; }
    exec('tar -C ' . escapeshellarg($raiz) . ' -xf ' . escapeshellarg($c) . ' 2>&1', $o, $rc);
    $log[$d] = ['restaurado_desde' => $c, 'rc' => $rc];
  }
}

$f = "$AQUI/informe-$modo-" . (count($doms) > 1 ? "varias" : ($doms[0] ?? "x")) . ".json";
if (is_file($f)) { $prev = json_decode(file_get_contents($f), true) ?: []; $log = $log + $prev; }
file_put_contents($f, json_encode($log, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
echo "ok $modo " . implode(',', $doms) . "\n";
