FROM python:3.12-slim

# Don't write .pyc files; send logs straight to `docker logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first so this layer stays cached until requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Run as a non-root user (OpenShift will insist on this later).
RUN useradd --uid 1001 --no-create-home appuser
USER 1001

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]