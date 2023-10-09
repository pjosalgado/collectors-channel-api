#!/bin/bash
docker buildx build --platform=linux/arm64 --push -t paulosalgado/collectors-channel-api:1.2.0 .
