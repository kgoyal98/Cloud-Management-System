# libvirt autoscaler

[![bjd2385](https://circleci.com/gh/bjd2385/autoscaler.svg?style=svg&circle-token=938cb53c2e72e9aa088b5adb106e9db6c4b68486)](https://github.com/bjd2385/autoscaler)

This project is a PoC for autoscaling via [libvirt](https://libvirt.org/) virtual machines (primarily KVM-based).

At the time I've started this project, while most public clouds offer autoscaling controllers, there don't appear to be _any_ open source initiatives, let alone one that utilizes the libvirt API. It's my opinion that many on-premise clouds may benefit from such a controller.

## Design

At this time, I'm hoping to cover the following items with an initial v0.1.0-release.

1. Collect metrics for disk IO, CPU and memory, provided by the libvirt API, and form a decision, based on a configuration file in YAML format /etc/autoscaler/autoscaler.yaml, whether or not to scale up or down, or wait an additional configured period before the daemon checks in on these metrics again.

    I'm still planning out the schema of the config file below.

    ```yaml
    version: v1
    scaling:
      databases:
        # State is where the ASGs current state is stored so it can be queried without making additional calls to libvirt.
        state:
          store:
            type: mysql
            connection:
            ip: localhost
            port: 3306
            credentials:
              env:
                username: $MYSQL_USERNAME
                password: $MYSQL_PASSWORD

        metrics:
          # Define where to store metrics: either in-memory or influxdb, since that's a time-series db I'm familiar with for now.
          store:
            type: local

          # store:
          #   type: influxdb
          #   url: http://localhost:8086/
          #   credentials:
          #     env:
          #       username: $INFLUXDB_USERNAME
          #       password: $INFLUXDB_PASSWORD

          # Seconds, minutes or hours between collecting metrics from all hosts on their VMs.
          interval: 30s

          # How often to evaluate all 'trailing' metrics.
          evaluate: 1m

          # Seconds, minutes or hours of collected metrics to cache and evaluate upon (must be >=interval)
          trailing: 21m

      hostGroups:
        group-1:
          # All hosts in group-1 should be pretty similar. Hosts differing by any great amount should be
          # managed as a separate group?
          - qemu+ssh:///system
          - qemu+ssh://domain-1/system
          - qemu+ssh://domain-2/system

      autoscalingGroups:
        # Unique keys defining separate VM groups to track. These keys should represent naming prefixes (?)
        rivendell:
          # This image and an associated libvirt template should exist on one of the hosts.
          image:
            name: template-ubuntu20.04-server
            # Options could be 'migrate' - migrate a copy of the domain to every host, or 'centralized' - hosts are using a centralized block store.
            imageMigration: migrate
            # Whether or not to delete the former image on all hosts but one.
            retention:
              strategy: delete
              keep:
          cloud-init:
            inline: |
              # Should contain an inline cloud-init script by which to customize VMs in this group, or you can specify a "file: "-keyword to read it from some location on-disk. All environment variables should be evaluated and replaced before bundling with the domains' disks?

            # file:

          # Group of hosts on which to provision VMs.
          hostGroup: group-1

          replacement:
            strategy: rollingupdate
            # replace one VM at a time if there's an image update in a group in this file, etc.
            maxUnavailable: 1

          networking:
            # A static IP range or list of IPs should be given to a group.
            addresses:
              - 192.168.5.2-192.168.5.254
            subnet: 255.255.255.0
            gateway: 192.168.1.1

          scaling:
            # maxNodes should not be larger than the number of IP addresses determined to be available in the range.
            maxNodes: 10
            minNodes: 3
            # Increment up or down by this many nodes any time a change is required to state.
            increment: 1
            # Seconds, minutes or hours until another action can be taken once a change is made. Basically puts a pause on metrics evaluation.
            cooldown: 5m

            metrics:
              # I need to work out how to determine percentages and such here. Disk IO isn't as straightforward. CPU could be based on VM load average? And memory could be based more-easily on a percentage.
              io: 80
              cpu: 80
              memory: 80
        mordor:
          ...

    ```

2. Provision new VMs on a list of hosts, reachable with the libvirt API.
    - Eventually, a strategy should be respected for placing VMs, such as round-robin (rr), resource-based (free resources) i.e. the host with the most free CPU, memory and disk IO should be selected), or first-come-first-utilized, so hosts are used one-by-one as necessary. Eventually, it would be neat if plugins could be used with this tool to control hosts as well (or maybe that's for a separate tool altogether).

3. A well-defined process should be laid out (maybe I should create a wiki for this project) for pairing libvirt domains with cloud-init scripts, so VMs can be customized before instantiation (cloud-init scripts updated) and VMs can be customized during boot. Networking at a minimum?

### Virtual disks

Disk images should be generalized with `virt-sysprep` and bundled with cloud-init scripts for customization.

### Databases

I'm thinking this tool should use at most two databases, including an influxdb time-series db for VM metrics, and a SQL database (probably just MySQL) for storing state. Both can easily be deployed as statefulsets on a k8s cluster, and they can certainly be deployed on a host of their own.

## Additional ideas / thoughts

1. A Flask endpoint should be available for VMs to authenticate and check in to make sure they're still healthy? Or even to check in when they're finally up.
2. What does DR look like if the autoscaling daemon goes down. We should be able to start it up again, since
all state is stored in a MySQL database.
