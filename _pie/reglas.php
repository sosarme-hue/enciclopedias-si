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
  'newtonpedia.com' => ['insertar' => '</footer>', 'html' => '<p>LINEA</p>'],
  'tenispedia.com' => ['insertar' => '</footer>', 'html' => '<p>LINEA</p>'],
  'cinematopedia.com' => ['sustituir' => '~ · ©\s*2026 Cinematopedia</p>~u', 'por' => '</p><p>LINEA</p>'],
  'pinacopedia.com' => ['sustituir' => '~ · ©\s*2026 Pinacopedia</p>~u', 'por' => '</p><p>LINEA</p>'],
  'filopedia.com' => ['sustituir' => '~ · ©\s*2026 Filopedia</p>~u', 'por' => '</p><p>LINEA</p>'],
  'medicapedia.org' => ['sustituir' => '~ · ©\s*2026 Medicapedia</p>~u', 'por' => '</p><p>LINEA</p>'],
  'classicapedia.com' => ['sustituir' => '~ · ©\s*2026 Classicapedia</p>~u', 'por' => '</p><p class="legales">LINEA</p>'],
];
