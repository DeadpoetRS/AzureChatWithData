#!/bin/bash

pip install --upgrade pip

pip install -r code/requirements.txt -r code/backend/requirements.txt 

pip install -r code/dev-requirements.txt

pre-commit install