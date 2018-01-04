#!/usr/bin/env bash
export PYTHONIOENCODING=utf-8
gunicorn --workers 2 --max-requests 1000 --keep-alive 6000 --timeout 0 --bind 0.0.0.0:8081 app:app