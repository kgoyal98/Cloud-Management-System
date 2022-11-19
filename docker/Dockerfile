ARG IMAGE=ubuntu:20.04

FROM ${IMAGE}

USER root

# Install the Doppler CLI via apt for secrets retrieval.
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl wget unzip gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | apt-key add - && \
    echo "deb https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

# Clean up for transport
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /autoscaler
COPY scripts/run.sh .

ENTRYPOINT [ "doppler", "run", "--" ]
CMD [ "./run.sh" ]
