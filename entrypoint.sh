#!/bin/bash
. .venv/bin/activate
uwsgi -T --http :9001 --uid www-data --gid www-data --enable-threads --wsgi-file ./main.py --callable app
