# BiteFlow — multi-stage image. Runtime layer carries no compilers, no
# dev tools, and runs as a non-root user.
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src ./src
COPY locales ./locales
COPY sql ./sql
COPY scripts ./scripts
COPY docker/entrypoint.sh ./docker/entrypoint.sh
# COPY preserves root-owned 660 modes; make everything readable by the
# non-root user and the entrypoint executable *before* dropping privileges.
RUN chown -R appuser:appuser /app \
    && chmod +x /app/docker/entrypoint.sh
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
ENTRYPOINT ["./docker/entrypoint.sh"]
