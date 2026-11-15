FROM python:3.12-slim

ARG REPO_URL=https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad.git

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 "$REPO_URL" /app/repo \
    && python -m pip install --no-cache-dir -e /app/repo/adversarial_lab \
    && python -m pip install --no-cache-dir "gradio>=5,<6"

COPY app.py /app/app.py

ENV ADVLAB_DATA_DIR=/tmp/advlab \
    PYTHONUNBUFFERED=1
WORKDIR /app/repo
EXPOSE 7860
CMD ["python", "/app/app.py"]
