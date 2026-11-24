FROM python:3.12.16-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv/sentinel-api

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 --create-home --home-dir /home/sentinel-api \
       --shell /usr/sbin/nologin sentinel-api

COPY --chown=10001:10001 app/ ./app/

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "from urllib.request import urlopen; r=urlopen('http://127.0.0.1:8000/api/v1/health', timeout=2); assert r.status == 200"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
