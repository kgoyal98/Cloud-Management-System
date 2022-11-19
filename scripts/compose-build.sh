#! /usr/bin/env bash
# Docker compose build of the docker/-directory.

(
    cd docker/ || exit 1 && \
    docker compose build
)
