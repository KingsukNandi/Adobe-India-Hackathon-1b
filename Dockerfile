# 1) Build React frontend
FROM node:18-alpine AS frontend
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm install --frozen-lockfile
COPY web/ .
RUN npm run build

# 2) Build Python backend
FROM python:3-slim AS backend

# Environment variables for Python and (optionally) HuggingFace offline mode
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir pandas numpy sentence-transformers pymupdf flask flask-cors gunicorn
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"


# Copy backend source code (preserve api/ as a package)
COPY api ./api
#COPY api/localmodel ./api/localmodel

# Copy React build into Flask’s static folder (inside api/static)
COPY --from=frontend /app/web/dist ./api/static

# Expose Flask port
EXPOSE 5000

# Start the Flask app with Gunicorn (module path is now api.app:app)
ENTRYPOINT ["sh", "-c", "exec gunicorn api.app:app --bind 0.0.0.0:5000"]