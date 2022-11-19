#! /usr/bin/env bash
# Docker compose up of the docker/-directory.

(
    cd docker/ || exit 1 && \
    DOPPLER_TOKEN="$(pass show doppler/autoscaler-sa)" docker compose up -d --build
)
