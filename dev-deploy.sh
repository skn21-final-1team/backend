#!/bin/bash


# tmux attach -t myserver


echo "기존 서버 종료 중..."
tmux kill-session -t myserver 2>/dev/null || true

echo "Git Change 진행 중..."
git switch devops

echo "Git Pull 진행 중..."
git fetch origin devops
git reset --hard origin/devops

echo "서버 재실행 중..."
tmux new-session -d -s myserver "source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"

echo "배포 완료!"