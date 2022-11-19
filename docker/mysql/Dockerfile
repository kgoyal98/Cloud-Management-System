ARG IMAGE=mysql:8.0.31
FROM ${IMAGE}

# Install the Doppler CLI via apt for secrets retrieval.
RUN (curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sh

# Wrap this Docker image in secrets we can pull from doppler.
ENTRYPOINT [ "doppler", "run", "--", "docker-entrypoint.sh" ]
CMD [ "mysqld" ]
