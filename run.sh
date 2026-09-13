#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SERVER_LOG="${SERVER_LOG:-$ROOT_DIR/server.log}"

cd "$ROOT_DIR"

if [[ ! -f ".env" ]]; then
  printf 'Erro: arquivo .env não encontrado em %s\n' "$ROOT_DIR" >&2
  exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  printf 'Erro: Python não encontrado.\n' >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import flask, dotenv, ibm_watson' >/dev/null 2>&1; then
  printf 'Dependências Python ausentes. Instalando requirements.txt...\n'
  "$PYTHON_BIN" -m pip install -r requirements.txt
fi

if [[ ! -d "mobile/node_modules" ]]; then
  printf 'Dependências do React Native ausentes. Instalando...\n'
  (cd mobile && npm install)
fi

if [[ -z "${EXPO_PUBLIC_API_URL:-}" ]]; then
  LOCAL_IP="$(hostname -I 2>/dev/null | cut -d ' ' -f1)"
  LOCAL_IP="${LOCAL_IP:-127.0.0.1}"
  export EXPO_PUBLIC_API_URL="http://${LOCAL_IP}:5000"
fi

if [[ "${1:-}" == "--import-actions" ]]; then
  printf 'Importando Actions pela API do Watson...\n'
  "$PYTHON_BIN" scripts/import_actions.py
  exit 0
fi

printf 'Iniciando Flask em http://0.0.0.0:5000\n'
printf 'API para o Expo: %s\n' "$EXPO_PUBLIC_API_URL"
printf 'Log do servidor: %s\n' "$SERVER_LOG"

"$PYTHON_BIN" src/server.py >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!

tail -n 0 -f "$SERVER_LOG" | while IFS= read -r line; do
  printf '[server] %s\n' "$line"
done &
SERVER_LOG_PID=$!

cleanup() {
  if kill -0 "$SERVER_LOG_PID" 2>/dev/null; then
    kill "$SERVER_LOG_PID" 2>/dev/null || true
  fi
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

sleep 2
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
  printf 'Erro: o Flask não iniciou. Consulte %s\n' "$SERVER_LOG" >&2
  exit 1
fi

printf 'Iniciando React Native/Expo diretamente na web. Pressione Ctrl+C para encerrar tudo.\n'
(cd mobile && npm start -- --web --lan)
