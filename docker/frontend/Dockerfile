# ── Base image ──────────────────────────────────────────────────────
FROM node:20-alpine

# ── Working directory ────────────────────────────────────────────────
WORKDIR /app

# ── Install dependencies ─────────────────────────────────────────────
COPY package.json package-lock.json* ./
RUN npm install

# ── Copy source ──────────────────────────────────────────────────────
COPY . .

# ── Expose Vite dev server port ──────────────────────────────────────
EXPOSE 5173