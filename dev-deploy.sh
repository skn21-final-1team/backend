#!/bin/bash


# tmux attach -t myserver


echo "기존 서버 종료 중..."
tmux kill-session -t myserver
tmux new -s myserver

echo "가상환경 실행 중..."
source ./venv/bin/activate

echo "Git Change 진행 중..."
git switch devops

echo "Git Pull 진행 중..."
git fetch origin devops
git reset --hard origin/devops

echo "서버 재실행 중..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4