#! /usr/bin/env bash
# Docker compose down

(
    cd docker || exit 1 && \
    docker compose down
)
