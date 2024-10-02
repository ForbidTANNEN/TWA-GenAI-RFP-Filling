#!/bin/bash
mkdir code
touch code/__init__.py

cp lambda_function.py code/lambda_function.py
cp -r utils code

cd code
zip -r finalBuild.zip *

aws lambda update-function-code \
    --function-name  twa-chatbot-LLMRetrieval \
    --zip-file fileb://finalBuild.zip

cd ..
rm -r code
rm finalBuild.zip