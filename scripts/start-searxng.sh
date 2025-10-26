#!/bin/bash
# Start SearXNG privacy-respecting metasearch engine (local, shared venv)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SEARXNG_DIR="${PROJECT_ROOT}/searxng"
PORT="${SEARXNG_PORT:-8181}"
BIND="${SEARXNG_BIND:-127.0.0.1}"
PID_FILE="${PROJECT_ROOT}/logs/searxng.pid"
LOG_FILE="${PROJECT_ROOT}/logs/searxng.log"
SHARED_VENV="${PROJECT_ROOT}/venv"
CONFIG_DIR="${PROJECT_ROOT}/config/searxng"
SETTINGS_FILE="${CONFIG_DIR}/settings.yml"
LIMITER_FILE="${CONFIG_DIR}/limiter.toml"
VALKEY_PID_FILE="${PROJECT_ROOT}/logs/valkey.pid"
VALKEY_LOG_FILE="${PROJECT_ROOT}/logs/valkey.log"
LIMITER_TEMPLATE="${SEARXNG_DIR}/searx/limiter.toml"

# Ensure logs directory exists early for consistent logging
mkdir -p "${PROJECT_ROOT}/logs"

# Prevent duplicate launches
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "SearXNG already running (PID: $OLD_PID) on ${BIND}:${PORT}."
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

if [ ! -d "$SEARXNG_DIR" ]; then
    echo "❌ SearXNG source not found at $SEARXNG_DIR"
    echo "Run: git submodule update --init searxng"
    exit 1
fi

if [ ! -d "$SHARED_VENV" ]; then
    echo "❌ Shared venv not found at $SHARED_VENV"
    echo "Run: cd $PROJECT_ROOT && python3 -m venv venv"
    exit 1
fi

source "${SHARED_VENV}/bin/activate"

mkdir -p "$CONFIG_DIR"

# Ensure we have an external settings file to keep submodule clean
if [ ! -f "$SETTINGS_FILE" ]; then
    cp "${SEARXNG_DIR}/utils/templates/etc/searxng/settings.yml" "$SETTINGS_FILE"
fi

# Bring limiter template alongside settings so rate limiting uses project config
if [ ! -f "$LIMITER_FILE" ] && [ -f "$LIMITER_TEMPLATE" ]; then
    cp "$LIMITER_TEMPLATE" "$LIMITER_FILE"
fi

# Install SearXNG into the shared environment if missing
if ! python - <<'PY' >/dev/null 2>&1
import importlib.util, sys
sys.exit(0 if importlib.util.find_spec("searx.webapp") else 1)
PY
then
    echo "Installing SearXNG dependencies into shared venv..."
    pip install --upgrade pip setuptools wheel
    pip install --upgrade pyyaml msgspec
    pip install --use-pep517 --no-build-isolation -e "${SEARXNG_DIR}"
fi

readarray -t SETTINGS_INFO < <(python - <<'PY' "$SETTINGS_FILE"
import secrets
import sys
from urllib.parse import urlparse

import yaml  # type: ignore

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as fh:
    data = yaml.safe_load(fh) or {}

server = data.setdefault("server", {})
secret = server.get("secret_key")
updated = False
if secret in (None, "", "ultrasecretkey"):
    server["secret_key"] = secrets.token_hex(32)
    updated = True

limiter_enabled = bool(server.get("limiter", False))
valkey_url = (data.get("valkey") or {}).get("url") or ""

if updated:
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)

if valkey_url:
    parsed = urlparse(valkey_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (6379 if parsed.scheme in ("valkey", "redis") else 6379)
else:
    host = ""
    port = ""

print(valkey_url)
print("true" if limiter_enabled else "false")
print(host)
print(port)
PY
)

VALKEY_URL="${SETTINGS_INFO[0]}"
LIMITER_ENABLED="${SETTINGS_INFO[1]:-false}"
VALKEY_HOST="${SETTINGS_INFO[2]:-127.0.0.1}"
VALKEY_PORT="${SETTINGS_INFO[3]:-6379}"

export SEARXNG_SETTINGS_PATH="$SETTINGS_FILE"

check_port_open() {
    python - "$1" "$2" <<'PY'
import socket
import sys

host = sys.argv[1]
port = sys.argv[2]

if not host or not port:
    raise SystemExit(1)

try:
    port_int = int(port)
except ValueError:
    raise SystemExit(1)

try:
    infos = socket.getaddrinfo(host, port_int, 0, socket.SOCK_STREAM)
except socket.gaierror:
    raise SystemExit(1)

for family, socktype, proto, _, sockaddr in infos:
    try:
        with socket.socket(family, socktype, proto) as sock:
            sock.settimeout(0.5)
            sock.connect(sockaddr)
            raise SystemExit(0)
    except OSError:
        continue

raise SystemExit(1)
PY
}

is_local_host() {
    case "$1" in
        127.*|localhost|::1|0.0.0.0) return 0 ;;
        "") return 1 ;;
        *) return 1 ;;
    esac
}

# Start an embedded Valkey/Redis when limiter is enabled and no server is reachable
if [ "$LIMITER_ENABLED" = "true" ]; then
    if [ -z "$VALKEY_URL" ]; then
        echo "⚠️ Limiter enabled but no valkey.url configured in $SETTINGS_FILE"
        exit 1
    fi

    if [ -f "$VALKEY_PID_FILE" ]; then
        EXISTING_VALKEY_PID=$(cat "$VALKEY_PID_FILE" 2>/dev/null || true)
        if [ -n "$EXISTING_VALKEY_PID" ] && ! ps -p "$EXISTING_VALKEY_PID" > /dev/null 2>&1; then
            rm -f "$VALKEY_PID_FILE"
        fi
    fi

    if ! check_port_open "$VALKEY_HOST" "$VALKEY_PORT"; then
        if is_local_host "$VALKEY_HOST"; then
            VALKEY_SERVER_BIN="$(command -v valkey-server || command -v redis-server || true)"
            if [ -z "$VALKEY_SERVER_BIN" ]; then
                echo "⚠️ Limiter requires Valkey but neither valkey-server nor redis-server is installed."
                exit 1
            fi

            echo "Starting local Valkey (${VALKEY_SERVER_BIN##*/}) on ${VALKEY_HOST}:${VALKEY_PORT}..."
            "$VALKEY_SERVER_BIN" --port "$VALKEY_PORT" --bind "$VALKEY_HOST" --daemonize yes \
                --pidfile "$VALKEY_PID_FILE" --save "" --appendonly no --logfile "$VALKEY_LOG_FILE"
            sleep 1
        else
            echo "⚠️ Cannot reach Valkey at ${VALKEY_HOST}:${VALKEY_PORT}. Update settings or start the service manually."
        fi
    fi

    ATTEMPTS=0
    until check_port_open "$VALKEY_HOST" "$VALKEY_PORT"; do
        ATTEMPTS=$((ATTEMPTS + 1))
        if [ "$ATTEMPTS" -ge 10 ]; then
            echo "✗ Valkey unavailable at ${VALKEY_HOST}:${VALKEY_PORT}. Aborting startup."
            exit 1
        fi
        sleep 0.5
    done
fi

if check_port_open "$BIND" "$PORT"; then
    echo "❌ Port ${BIND}:${PORT} already in use. Abort."
    exit 1
fi

echo "Starting SearXNG on ${BIND}:${PORT}..."

export FLASK_APP="searx.webapp"

nohup "${SHARED_VENV}/bin/flask" run --host="${BIND}" --port="${PORT}" > "$LOG_FILE" 2>&1 &

SEARXNG_PID=$!
echo "$SEARXNG_PID" > "$PID_FILE"

sleep 3

if ps -p "$SEARXNG_PID" > /dev/null 2>&1; then
    echo "✓ SearXNG started successfully!"
    echo "   PID: $SEARXNG_PID"
    echo "   URL: http://${BIND}:${PORT}"
    echo "   Logs: ${LOG_FILE}"
else
    echo "✗ Failed to start SearXNG. Check logs: ${LOG_FILE}"
    rm -f "$PID_FILE"
    exit 1
fi