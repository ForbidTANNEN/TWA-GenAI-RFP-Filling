#!/bin/bash

pip install -r lambda-dependency-requirements.txt --platform manylinux2014_x86_64 --python-version 3.11 --target ./python --only-binary=:all:

zip -r python.zip python
rm python