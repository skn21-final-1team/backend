FROM python:3.12-alpine AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --frozen --no-install-project --no-dev


FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . /app

RUN apk add --no-cache openssh-server bash && \
    mkdir -p /run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    ssh-keygen -A

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 80 22

CMD sh -c "/usr/sbin/sshd && uvicorn main:app --host 0.0.0.0 --port 80"