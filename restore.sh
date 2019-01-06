#!/bin/bash

echo "==> Removing all data from the database..."
python manage.py flush --noinput

echo "==> Loading user fixtures..."
python manage.py loaddata services/fixtures/users.json

echo "==> Loading services fixtures..."
python manage.py loaddata services/fixtures/services.json

echo "==> Done!"
