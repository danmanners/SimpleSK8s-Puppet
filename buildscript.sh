#!/bin/bash
# Runs black for code quality adherance to PEP8
black simplesk8s.py --line-length=120
black functions/ --line-length=120
black questions/ --line-length=120
# Builds the code
pyinstaller simplesk8s.py --noconfirm --add-data setup/:setup --onefile
