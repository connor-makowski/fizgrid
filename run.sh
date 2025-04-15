#!/bin/bash
docker build . --tag "fizgrid" --quiet > /dev/null
# if an arg was passed: use it as an entrypoint
if [ -z "$1" ]; then
    docker run -it --rm \
        --volume "$(pwd):/app" \
        "fizgrid"
else
    docker run -it --rm \
        --volume "$(pwd):/app" \
        --entrypoint "/app/utils/$1.sh" \
        "fizgrid"
fi