# steps
- Have a fully running application

- build image
    - write: " docker image build -t IMAGE_NAME . "
    - write: " docker image build -t music-ai . "

- build continer
    - write: " docker run --rm -d --network=host  music-ai:latest  "


- ID created with container
    - docker logs CONTAINER_ID



[ VSCODE HAS A GREAT DOCKER EXTENTION TO GLANCE AT ENV ]

# Display all Images
- docker images

# Display all Running Containers
- docker container ls


# FREE ALL LOOSE UNUSED IMAGES AND CONTAINERS
- docker system prune