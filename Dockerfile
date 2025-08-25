FROM python:3.10-slim
LABEL maintainer="nahuelement"

ENV PYTHONUNBUFFERED=1
ENV PATH="/scripts:/py/bin:$PATH"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Crear entorno virtual
RUN python -m venv /py && /py/bin/pip install --upgrade pip

# Instalar dependencias del sistema necesarias para Django y Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        curl \
        wget \
        git \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpangocairo-1.0-0 \
        libpango-1.0-0 \
        libgtk-3-0 \
        libharfbuzz0b \
        libgdk-pixbuf-xlib-2.0-0 \
        libxcb1 \
        ca-certificates \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no root
RUN adduser --disabled-password --gecos "" django-user \
    && mkdir -p /vol/web/media /vol/web/static /tmp/playwright-download \
    && chown -R django-user:django-user /vol \
    && chmod -R 755 /vol \
    && chmod -R 777 /tmp/playwright-download /tmp

# Copiar requirements y scripts
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app

WORKDIR /app
EXPOSE 8000

# Instalar dependencias Python
ARG DEV=false
RUN /py/bin/pip install --upgrade pip wheel && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    rm -rf /tmp/*

# Instalar navegadores Playwright
RUN /py/bin/pip install playwright && \
    /py/bin/playwright install chromium

# Permisos finales
RUN chmod -R +x /scripts

USER django-user

CMD ["run.sh"]
