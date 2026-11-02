#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd factory_project
python manage.py collectstatic --no-input
python manage.py migrate
