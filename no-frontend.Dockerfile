
# This image will build superset with the pre-built frontend. So it will NOT run npm ci & npm build
FROM python:3.10-slim-bookworm

WORKDIR /app
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    SUPERSET_ENV=production \
    FLASK_APP="superset.app:create_app()" \
    PYTHONPATH="/app/pythonpath" \
    SUPERSET_HOME="/app/superset_home" \
    SUPERSET_PORT=8088

RUN mkdir -p ${PYTHONPATH} superset/static requirements superset-frontend apache_superset.egg-info requirements \
    && useradd --user-group -d ${SUPERSET_HOME} -m --no-log-init --shell /bin/bash superset \
    && apt-get update -qq && apt-get install -yqq --no-install-recommends \
        curl \
        default-libmysqlclient-dev \
        libsasl2-dev \
        libsasl2-modules-gssapi-mit \
        libpq-dev \
        libecpg-dev \
        libldap2-dev \
    && touch superset/static/version_info.json \
    && chown -R superset:superset ./* \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=superset:superset pyproject.toml setup.py MANIFEST.in README.md ./

# Install GeckoDriver WebDriver and Firefox
ARG GECKODRIVER_VERSION=v0.34.0 \
    FIREFOX_VERSION=137.0.1

RUN apt-get update -qq \
    && apt-get install -yqq --no-install-recommends wget bzip2 xz-utils \
    && ARCH=$(uname -m) \
    && if [ "$ARCH" = "x86_64" ]; then \
        GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz"; \
        FIREFOX_URL="https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.bz2"; \
        TAR_EXTRACT="tar xfj"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux-aarch64.tar.gz"; \
        FIREFOX_URL="https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-aarch64/en-US/firefox-${FIREFOX_VERSION}.tar.xz"; \
        TAR_EXTRACT="tar xfJ"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi \
    && wget -q "$GECKODRIVER_URL" -O - | tar xfz - -C /usr/local/bin \
    && wget -q "$FIREFOX_URL" -O - | $TAR_EXTRACT - -C /opt \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && apt-get autoremove -yqq --purge wget bzip2 xz-utils \
    && rm -rf /var/[log,tmp]/* /tmp/* /var/lib/apt/lists/*

# setup.py uses the version information in package.json
COPY --chown=superset:superset superset-frontend/package.json superset-frontend/
COPY --chown=superset:superset requirements/base.txt requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    apt-get update -qq && apt-get install -yqq --no-install-recommends \
      build-essential \
    && pip install --upgrade setuptools pip \
    && pip install -r requirements/base.txt \
    && apt-get autoremove -yqq --purge build-essential \
    && rm -rf /var/lib/apt/lists/*

## Lastly, let's install superset itself
COPY --chown=superset:superset superset superset
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -e .

# Compile translations for the backend - this generates .mo files, then deletes the .po files
COPY ./scripts/translations/generate_mo_files.sh ./scripts/translations/
RUN ./scripts/translations/generate_mo_files.sh \
    && chown -R superset:superset superset/translations \
    && rm superset/translations/messages.pot \
    && rm superset/translations/*/LC_MESSAGES/*.po

COPY --chmod=755 ./docker/run-server.sh /usr/bin/
USER superset

HEALTHCHECK CMD curl -f "http://localhost:${SUPERSET_PORT}/health"

EXPOSE ${SUPERSET_PORT}

CMD ["/usr/bin/run-server.sh"]
