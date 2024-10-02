#!/bin/bash

# Set the S3 bucket name
BUCKET_NAME="twa-chatbot-chatbot-software"

# Directory containing the files to upload
DIRECTORY="code"

# Clear the bucket before uploading new files
echo "Clearing the bucket: $BUCKET_NAME..."
aws s3 rm "s3://$BUCKET_NAME/" --recursive

cd $DIRECTORY

echo "Starting upload of website content to $BUCKET_NAME..."
aws s3 sync . "s3://$BUCKET_NAME/" --exclude "*" --include "*.html" --include "*.js" --include "*.css" --include "*.png" --include "*.jpg" ---include "*.gif"-include "*/"

echo "Upload complete."

aws cloudfront create-invalidation --distribution-id EPJ8Y9J7TDY16 --paths "/*"