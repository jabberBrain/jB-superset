
# if BUILDPLATFORM is null, set it to 'amd64' (or leave as is otherwise).
ARG BUILDPLATFORM=${BUILDPLATFORM:-amd64}
FROM --platform=${BUILDPLATFORM} node:18-bullseye-slim AS superset-node

# Somehow we need python3 + build-essential on this side of the house to install node-gyp
RUN apt-get update -qq \
    && apt-get install \
        -yqq --no-install-recommends \
        build-essential \
        python3

        
        RUN --mount=type=bind,target=/frontend-mem-nag.sh,src=./docker/frontend-mem-nag.sh \
        /frontend-mem-nag.sh
        
# NPM ci first, as to NOT invalidate previous steps except for when package.json changes
WORKDIR /app/superset-frontend
RUN --mount=type=bind,target=./package.json,src=./superset-frontend/package.json \
    --mount=type=bind,target=./package-lock.json,src=./superset-frontend/package-lock.json \
    npm ci

COPY superset-frontend /app/superset-frontend

ENV BUILD_CMD=build
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Runs the webpack build process
RUN npm run ${BUILD_CMD}

# This copies the .po files needed for translation
RUN mkdir -p /app/superset/translations
COPY superset/translations /app/superset/translations

# Compiles .json files from the .po files, then deletes the .po files
RUN npm run build-translation
RUN rm /app/superset/translations/*/LC_MESSAGES/*.po
RUN rm /app/superset/translations/messages.pot

# Final stage
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

# setup.py uses the version information in package.json
COPY --chown=superset:superset superset-frontend/package.json superset-frontend/
COPY --chown=superset:superset requirements/base.txt requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    apt-get update -qq && apt-get install -yqq --no-install-recommends \
      build-essential \
    && pip install --upgrade setuptools pip \
    && pip install -r requirements/base.txt \
    && pip install psycopg2-binary \
    && apt-get autoremove -yqq --purge build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the compiled frontend assets
COPY --chown=superset:superset --from=superset-node /app/superset/static/assets superset/static/assets

## Lastly, let's install superset itself
COPY --chown=superset:superset superset superset
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -e .

# Copy jabberBrain assets
COPY --chown=superset:superset ./assets /app/superset/static/jb_assets

# Add entrypoints, superset_config, etc
COPY --chown=superset:superset ./docker /app/docker

# Copy the .json translations from the frontend layer
COPY --chown=superset:superset --from=superset-node /app/superset/translations superset/translations

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