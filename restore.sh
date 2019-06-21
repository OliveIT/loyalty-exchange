#!/bin/bash

echo "==> Removing all data from the database..."
python manage.py flush --noinput

echo "==> Loading user fixtures..."
python manage.py loaddata services/fixtures/users.json

echo "==> Loading user email fixtures..."
python manage.py loaddata services/fixtures/account.emailaddress.json

echo "==> Done!"
