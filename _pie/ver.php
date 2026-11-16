<?php
// Muestra el pie (footer) tal como se ve en las guías WordPress .si. Solo lectura.
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
$ctx = stream_context_create(['http' => ['timeout' => 20, 'user_agent' => 'Mozilla/5.0 (pie)'], 'ssl' => ['verify_peer' => true]]);
foreach (['sitges','santperederibes','castelldefels','santcugat','vilanova','garraf','eivissa'] as $d) {
  $h = @file_get_contents("https://$d.si/", false, $ctx);
  echo "== $d.si (" . strlen((string)$h) . " bytes)\n";
  if (!$h) continue;
  $i = strripos($h, '<footer'); $j = strripos($h, '</footer>');
  $f = $i !== false ? substr($h, $i, ($j !== false ? $j + 9 : $i + 3000) - $i) : '(sin <footer>) ' . substr($h, -2500);
  $f = preg_replace('~<(script|style|svg)\b.*?</\1>~is', '', $f);
  $f = preg_replace('/\s+/', ' ', $f);
  echo mb_substr($f, 0, 2200), "\n";
  if (preg_match_all('/.{0,100}(?:©|&copy;|&#169;).{0,100}/u', $h, $m)) echo "COPY: ", implode(' || ', array_slice($m[0], 0, 3)), "\n";
}
