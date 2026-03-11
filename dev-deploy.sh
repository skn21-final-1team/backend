#!/bin/bash

set -euo pipefail

# tmux attach -t myserver

#8000번 포트를 사용하는 프로세스가 있다면 강제 종료 (PID 확인 후 kill)
if ! command -v lsof &> /dev/null; then
    echo "lsof가 설치되어 있지 않아 8000 포트 정리를 건너뜁니다."
else
    PORT_8000_PIDS=$(lsof -t -i:8000 2>/dev/null || true)
    if [ -z "$PORT_8000_PIDS" ]; then
        echo "No process running on port 8000"
    else
        echo "Killing process $PORT_8000_PIDS on port 8000"
        kill -9 $PORT_8000_PIDS
    fi
fi

echo "기존 서버 종료 중..."
tmux kill-session -t myserver 2>/dev/null || true

echo "Git Change 진행 중..."
git -c safe.directory=/home/ubuntu/workspace switch devops

echo "Git Pull 진행 중..."
git -c safe.directory=/home/ubuntu/workspace fetch origin devops
git -c safe.directory=/home/ubuntu/workspace reset --hard origin/devops

echo "의존성 설치 중..."
source .venv/bin/activate

# uv가 설치되어 있는지 확인
if command -v uv &> /dev/null; then
    echo "uv 사용하여 의존성 설치"
    uv pip install -r pyproject.toml
else
    echo "uv가 설치되어 있지 않습니다. pip 사용"
    pip install -r pyproject.toml
fi

echo "서버 재실행 중..."
if ! command -v tmux &> /dev/null; then
    echo "ERROR: tmux가 설치되어 있지 않습니다."
    exit 1
fi

tmux new-session -d -s myserver "source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"

echo "배포 완료!"
