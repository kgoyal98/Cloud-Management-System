ARG IMAGE=influxdb:2.5.1

FROM ${IMAGE}

# Install the Doppler CLI via apt for secrets retrieval.
RUN (curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sh

ENTRYPOINT [ "doppler", "run", "--", "/entrypoint.sh" ]
CMD [ "influxd" ]
