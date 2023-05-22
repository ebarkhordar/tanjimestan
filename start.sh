#!/bin/sh
git pull origin main
pkill -9 -f main.py
python3 main.py