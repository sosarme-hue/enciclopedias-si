<?php
/*
 * Plugin Name: Pie de licencia (CC BY-NC 4.0)
 * Description: Pone «© 2026 Alejandro Rosàs · Contenido bajo licencia CC BY-NC 4.0, salvo indicación en contrario» en el pie, en lugar de «© 2026 <Guía> Sí · <dominio> ·». Para quitarlo, borra este archivo.
 */
if (!defined('ABSPATH')) exit;
add_action('template_redirect', function () {
  if (is_admin() || is_feed() || (function_exists('wp_doing_ajax') && wp_doing_ajax()) || (defined('REST_REQUEST') && REST_REQUEST)) return;
  ob_start('pie_licencia_cc');
}, 1);
function pie_licencia_cc($h) {
  if (!is_string($h) || $h === '' || strpos($h, 'creativecommons.org/licenses/by-nc/4.0') !== false) return $h;
  $i = strripos($h, '<footer id="colophon"'); if ($i === false) return $h;
  $T = [
    'es' => ['Contenido bajo licencia', 'salvo indicación en contrario'],
    'ca' => ['Contingut sota llicència', "llevat que s'indiqui el contrari"],
    'en' => ['Content licensed under', 'unless otherwise noted'],
  ];
  $l = 'es'; if (preg_match('/<html[^>]*\blang="([a-zA-Z]{2})/', $h, $m)) $l = strtolower($m[1]);
  if (!isset($T[$l])) $l = 'es';
  $linea = '© 2026 Alejandro Rosàs · ' . $T[$l][0] . ' <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.' . $l . '" rel="license noopener" style="display:inline">CC BY-NC 4.0</a>, ' . $T[$l][1] . ' · ';
  $pie = substr($h, $i);
  $nuevo = preg_replace('~(<span>)©\s*\d{4}\s+[^<·]{1,60}?\s·\s[a-z0-9.-]{1,40}\.si\s·\s~u', '$1' . str_replace(['\\', '$'], ['\\\\', '\\$'], $linea), $pie, 1);
  if (!is_string($nuevo) || $nuevo === $pie) return $h;
  return substr($h, 0, $i) . $nuevo;
}
