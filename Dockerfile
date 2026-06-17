# Intentional insecure Docker readiness for DevSecOps demos:
# - Runs as root by default.
# - Uses Flask's debug-capable development server.
# - Enables INSECURE_DEBUG by default.
# Secure version notes: create a non-root user, disable debug, use Gunicorn,
# pin and scan base images, and apply runtime limits.
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV INSECURE_DEBUG=1
EXPOSE 5000

CMD ["python", "app.py"]
