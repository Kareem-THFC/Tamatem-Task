# The frontend is a static bundle and the backend is a Python service, but the
# hiring demo is a single URL: Flask serves the built bundle alongside /api, so
# there is one deploy, one origin, and no CORS in production.

# --- Stage 1: build the React bundle ------------------------------------------
FROM node:22-alpine AS frontend

WORKDIR /frontend

# Copied before the sources so a change to application code does not invalidate
# the cached dependency install.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# .env.production points the client at its own origin; see that file.
RUN npm run build

# --- Stage 2: the Flask service ------------------------------------------------
FROM python:3.12-slim

# Unbuffered output so container logs appear in Render's stream immediately.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY items.csv ./items.csv

# The bundle lands outside app/static so it cannot collide with openapi.json,
# which is already served from there.
COPY --from=frontend /frontend/dist ./app/frontend_dist

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Render injects PORT; the default matches its convention for local runs.
ENV PORT=10000
EXPOSE 10000

ENTRYPOINT ["docker-entrypoint.sh"]
