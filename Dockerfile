FROM python:3.11-slim

WORKDIR /app

# Create a non-root user to reduce attack surface
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies before copying app code (improves layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY downloader_core.py app.py ./

# Create output directory and set ownership so appuser can write to it
RUN mkdir -p /data/transcripts && chown -R appuser:appuser /data /app

USER appuser

# OUTPUT_DIR is the root for all generated transcript folders/files.
# Override this when the default mount point differs.
ENV OUTPUT_DIR="/data/transcripts"

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
