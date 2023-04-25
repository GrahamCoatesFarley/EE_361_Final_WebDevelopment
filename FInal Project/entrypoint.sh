#!/bin/bash
echo "Setting up and Running the Application"
python manage.py migrate
python manage.py runserver "0.0.0.0:8000"