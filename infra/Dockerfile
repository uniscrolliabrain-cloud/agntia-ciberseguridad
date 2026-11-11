ARG PYTHON_BASE
FROM ${PYTHON_BASE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY wheelhouse /wheels
COPY requirements.lock /requirements.lock
RUN --network=none python -m pip install --no-index --no-cache-dir --require-hashes --find-links=/wheels -r /requirements.lock && rm -rf /wheels && mkdir /state && chown 65532:65532 /state
USER 65532:65532
WORKDIR /state
EXPOSE 8012
ENTRYPOINT ["agntia-ciberseguridad"]
CMD ["serve", "--config", "/run/config/server.json", "--host", "0.0.0.0", "--port", "8012"]
