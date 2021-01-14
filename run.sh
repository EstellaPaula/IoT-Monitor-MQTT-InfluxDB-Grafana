#!/bin/bash

# Build new image
docker-compose -f stack.yml build

# Init swarm
docker swarm init

# Deploy stack
docker stack deploy -c stack.yml sprc3