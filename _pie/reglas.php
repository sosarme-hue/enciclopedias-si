<?php
// Dónde va la línea de copyright y licencia en cada web (LINEA = la línea en el idioma de la página).
return [
  'mythicapedia.com' => ['insertar' => '</footer>', 'html' => '<p>LINEA</p>'],
  'iapedia.si' => ['insertar' => "\n  </div>\n</footer>", 'html' => "\n    <p>LINEA</p>"],
  'celebraciones.org' => ['sustituir' => '~(<div class="wrap legalpie">)©\s*2026\s*celebraciones\.org~u', 'por' => '$1LINEA'],
  'catdogpedia.com' => ['insertar' => '</footer>', 'html' => '<p class="fuentes">LINEA</p>'],
  'ludicopedia.com' => ['solo' => ['js/comun.js'], 'sustituir' => '~(Créditos de las fotos</a></nav>)(</div>`;)~u', 'por' => '$1<div style="margin-top:.6em">LINEA</div>$2'],
  'zodiacopedia.com' => ['insertar' => '</footer>', 'html' => '<br>LINEA'],
  'culinapedia.com' => ['insertar' => '</footer>', 'html' => '<p>LINEA</p>'],
];
