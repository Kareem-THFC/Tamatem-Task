#!/bin/sh
# Container start-up: bring the schema up to date, make sure the demo data the
# reviewer needs is present, then hand the process over to gunicorn.
#
# Both seeding steps are idempotent -- the importer upserts by external id and
# the demo user is created or reset -- so this is safe to run on every boot,
# including the restarts a free instance goes through.
set -e

echo "==> Applying migrations"
flask --app run db upgrade

echo "==> Importing catalogue"
flask --app run import-products items.csv

echo "==> Seeding demo user"
flask --app run seed-demo-user

echo "==> Starting gunicorn on port ${PORT}"
# exec replaces the shell so gunicorn receives SIGTERM directly and shuts down
# cleanly when the platform recycles the instance.
exec gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers 2 \
  --threads 4 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  "app:create_app()"
