# MFL Transaction Monitor Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY main.py .
COPY scripts/ ./scripts/

# Create data directory
RUN mkdir -p data

# Create non-root user
RUN useradd -m -u 1000 mfluser && chown -R mfluser:mfluser /app
USER mfluser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.mfl_monitor.utils.config import Config; exit(0 if Config.validate() else 1)"

# Default command
CMD ["python", "main.py"]
