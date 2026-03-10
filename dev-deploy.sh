#!/bin/bash
set -euo pipefail

export PATH="/home/ubuntu/.local/bin:/home/ubuntu/.cargo/bin:${PATH}"

ensure_uv_command() {
    if command -v uv >/dev/null 2>&1; then
        return 0
    fi
    echo "uv 바이너리를 찾을 수 없습니다. 현재 PATH: ${PATH}" >&2
    return 1
}

# tmux attach -t myserver

#8000번 포트를 사용하는 프로세스가 있다면 강제 종료 (PID 확인 후 kill)
PID=$(lsof -t -i:8000)
if [ -z "$PID" ]; then
    echo "No process running on port 8000"
else
    echo "Killing process $PID on port 8000"
    kill -9 $PID
fi

echo "기존 서버 종료 중..."
tmux kill-session -t myserver 2>/dev/null || true

echo "Git Change 진행 중..."
git -c safe.directory=/home/ubuntu/workspace switch devops

echo "Git Pull 진행 중..."
git -c safe.directory=/home/ubuntu/workspace fetch origin devops
git -c safe.directory=/home/ubuntu/workspace reset --hard origin/devops

echo "의존성 설치 중..."
ensure_uv_command
source .venv/bin/activate
uv pip install -r pyproject.toml

echo "서버 재실행 중..."
tmux new-session -d -s myserver "source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"

echo "배포 완료!"
