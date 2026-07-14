#!/usr/bin/env bash

docker compose -f docker-compose-dev.yml run --rm backend pre-commit run --all-files