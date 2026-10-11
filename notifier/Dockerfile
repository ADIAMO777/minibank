FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

RUN useradd --uid 1001 --no-create-home appuser
USER 1001

# No EXPOSE: this container doesn't listen on any port.
CMD ["python", "worker.py"]