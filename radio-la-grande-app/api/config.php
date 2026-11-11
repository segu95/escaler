<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
$path = dirname(__DIR__) . '/storage/config.json';
if (!is_file($path)) { http_response_code(503); echo json_encode(['error'=>'Configuración no disponible']); exit; }
readfile($path);
