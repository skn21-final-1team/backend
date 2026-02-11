#!/bin/bash

if [ -n "$SSH_PUBLIC_KEY" ]; then
    echo "$SSH_PUBLIC_KEY" > /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
fi

/usr/sbin/sshd

exec uvicorn main:app --host 0.0.0.0 --port 80
