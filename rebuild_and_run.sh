#!/bin/bash

# Zmienna dla nazwy obrazu i kontenera
IMAGE_NAME="ffmpeg-gui"
CONTAINER_NAME="ffmpeg-gui"

# Usuń stary kontener, jeśli istnieje
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    docker rm -f ${CONTAINER_NAME}
fi

# Usuń stary, nieużywany obraz, jeśli istnieje
if [ "$(docker images -q ${IMAGE_NAME})" ]; then
    docker rmi ${IMAGE_NAME}
fi

# Zbuduj nowy obraz Docker
docker build -t ${IMAGE_NAME} .

# Uruchom nowy kontener
docker run --name ${CONTAINER_NAME} -p 8080:8080 -v $(pwd)/uploads:/app/uploads -v $(pwd)/temp:/app/temp -v $(pwd)/gifs:/app/gifs ${IMAGE_NAME}

# Usuń stary, nieużywany obraz
docker image prune -f
