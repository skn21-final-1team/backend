# Use a Python image with uv pre-installed
FROM python:3.12-alpine AS builder

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy the project files
# Copy only the files necessary for dependency installation first to leverage caching
COPY pyproject.toml uv.lock ./

RUN pip install uv

# Install the project's dependencies using the lockfile and pyproject.toml
RUN uv sync --frozen --no-install-project --no-dev



# Final stage
FROM python:3.12-alpine

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY . /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
