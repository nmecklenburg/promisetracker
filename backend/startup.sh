#!/usr/bin/bash

python ptracker/seed.py

fastapi dev ptracker/main.py
