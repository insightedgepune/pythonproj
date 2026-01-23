#!/bin/bash
# push-pythonproj.sh

USERNAME="310383"
IMAGE_NAME="pythonproj-app"
VERSION="1.0"

echo "Step 1: Logging into Docker Hub..."
docker login -u $USERNAME

echo "Step 2: Tagging image..."
docker tag $IMAGE_NAME:latest $USERNAME/$IMAGE_NAME:latest
docker tag $IMAGE_NAME:latest $USERNAME/$IMAGE_NAME:$VERSION

echo "Step 3: Pushing to Docker Hub..."
docker push $USERNAME/$IMAGE_NAME:latest
docker push $USERNAME/$IMAGE_NAME:$VERSION

echo "Step 4: Verifying..."
docker pull $USERNAME/$IMAGE_NAME:latest

echo " Done! Your image is available at:"
echo "https://hub.docker.com/r/$USERNAME/$IMAGE_NAME"
