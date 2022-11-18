#! /bin/bash

asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin-add yarn   https://github.com/twuni/asdf-yarn.git
asdf plugin-add protoc https://github.com/paxosglobal/asdf-protoc.git

asdf install

if [ "$(conda info --envs --json | jq -r '.envs[]' | awk '/(autoscaler)$/')" = "" ]; then
    conda create -y -n autoscaler python=3.10
fi

sudo apt install -y bats libvirt-dev

conda activate autoscaler
#pip install setupext_janitor pylint mypy
