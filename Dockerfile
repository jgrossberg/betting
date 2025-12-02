FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY betting/ betting/

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Cloud Run sets PORT env var
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn betting.api.http_api:app --host 0.0.0.0 --port $PORT"]
