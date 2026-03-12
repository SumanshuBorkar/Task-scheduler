# ── Base image ──────────────────────────────────────────────────────
FROM python:3.13-slim

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr (important for logs)
ENV PYTHONUNBUFFERED=1

# ── System dependencies ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ──────────────────────────────────────
# Copy requirements first — Docker caches this layer if requirements don't change
COPY requirements/base.txt requirements/base.txt
COPY requirements/development.txt requirements/development.txt
RUN pip install --upgrade pip \
    && pip install -r requirements/development.txt

# ── Copy project source ──────────────────────────────────────────────
COPY . .

# ── Expose port ──────────────────────────────────────────────────────
EXPOSE 8000