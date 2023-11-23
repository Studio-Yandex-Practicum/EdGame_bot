#!/bin/sh

alembic upgrade head

python edgame.py
