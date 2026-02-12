#!/bin/bash


# tmux attach -t myserver

echo "change directory to backend"
cd workspace

echo "기존 서버 종료 중..."
tmux kill-session -t myserver
tmux new -s myserver

echo "Git Change 진행 중..."
git switch devops

echo "Git Pull 진행 중..."
git pull

echo "서버 재실행 중..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4