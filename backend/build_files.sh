#!/bin/bash
pip install -r backend/requirements.txt
cd backend
python manage.py collectstatic --noinput
python manage.py migrate --no-input