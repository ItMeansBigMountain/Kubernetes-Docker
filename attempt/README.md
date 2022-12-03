# Container Steps
- Have a fully running application

- build image
    - write: " docker image build -t IMAGE_NAME . "
    - write: " docker image build -t music-ai . "

- build continer
    - write: " docker run --rm -d --network=host  IMAGE_NAME:latest  "
    - write: " docker run --rm -d --network=host  music-ai:latest  "
    - ID created with container

[ VSCODE HAS A GREAT DOCKER EXTENTION TO GLANCE AT ENV ]

# Cluster Steps
- ...



### Display Container Logs
- docker logs CONTAINER_ID

### Display all Images
- docker images

### Display all Running Containers
- docker container ls

### FREE LOOSE IMAGES & CONTAINERS
- docker system prune