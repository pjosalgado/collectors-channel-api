#!/bin/bash
docker run -d -p 5000:5000 --name collectors-channel-api --env-file=.env paulosalgado/collectors-channel-api:1.3.0
