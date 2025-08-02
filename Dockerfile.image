FROM apache/superset:4.1.3


USER root

# Install psycopg2-binary for PostgreSQL
RUN pip install psycopg2-binary

# Copy custom frontend assets
COPY --chown=superset:superset ./superset /app/superset
COPY --chown=superset:superset ./assets /app/superset/static/jb_assets
COPY --chown=superset:superset ./docker /app/docker

# Switch back to the superset user
USER superset

CMD ["/app/docker/entrypoints/run-server.sh"]