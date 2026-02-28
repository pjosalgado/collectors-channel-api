#!/bin/bash
docker buildx build --platform=linux/amd64,linux/arm64 --push -t paulosalgado/collectors-channel-api:1.3.1 .
