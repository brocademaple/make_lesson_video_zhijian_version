#!/bin/zsh
set -eu
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR"
if [[ ! -x .venv/bin/any2video ]]; then
  print "请先安装：python3 -m venv .venv && .venv/bin/pip install -e ."
  read "?按回车退出"
  exit 1
fi
if [[ ! -x ppt_course_renderer/node_modules/.bin/remotion ]]; then
  print "视频导出依赖尚未安装：cd ppt_course_renderer && npm ci"
fi
ANY2VIDEO_PORT=$(.venv/bin/python - <<'PY'
import json, socket, urllib.request
for port in range(8878, 8899):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/openapi.json', timeout=.3) as response:
            if json.load(response).get('info', {}).get('title') == 'any2video API':
                print(f'reuse:{port}')
                break
    except Exception:
        pass
    with socket.socket() as candidate:
        try:
            candidate.bind(('127.0.0.1', port))
        except OSError:
            continue
        print(f'start:{port}')
        break
else:
    raise SystemExit('8878–8898 都被占用，请先释放一个端口。')
PY
)
START_MODE="${ANY2VIDEO_PORT%%:*}"
ANY2VIDEO_PORT="${ANY2VIDEO_PORT##*:}"
ANY2VIDEO_URL="http://127.0.0.1:$ANY2VIDEO_PORT/"
if [[ "$START_MODE" == start ]]; then
  .venv/bin/any2video serve --host 127.0.0.1 --port "$ANY2VIDEO_PORT" --no-reload &
  SERVER_PID=$!
  trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT INT TERM
  .venv/bin/python - "$ANY2VIDEO_URL" <<'PY'
import sys, time, urllib.request
for _ in range(100):
    try:
        with urllib.request.urlopen(sys.argv[1] + 'api/health', timeout=.5) as response:
            if response.status == 200:
                break
    except Exception:
        time.sleep(.2)
else:
    raise SystemExit('工作台未能启动，请查看终端日志。')
PY
fi
print "any2video 已打开：$ANY2VIDEO_URL"
open -a Comet "$ANY2VIDEO_URL" 2>/dev/null || open "$ANY2VIDEO_URL"
if [[ "$START_MODE" == start ]]; then
  print "保持此窗口开启；按 Ctrl+C 停止。"
  wait "$SERVER_PID"
fi
