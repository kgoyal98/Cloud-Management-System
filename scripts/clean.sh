#! /bin/bash
# Clean up installed files.

python setup.py clean --all

##
# Clear all containers and unused images. Useful after you've just tested a Dockerfile build a bunch of times.
clear_containers()
{
    # Clear containers.
    for c in $(docker ps -a | awk '{ print $1 }' | tail -n +2)
    do
        docker rm "$c"
    done

    # Clear images.
    for im in $(docker images | awk '{ print $3 }' | tail -n +2)
    do
        docker rmi "$im"
    done

    return 0
}

clear_containers

unset -f clear_containers
