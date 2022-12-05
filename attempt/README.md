# Container Steps
- Have a fully running application

- build image
    - write: " docker image build -t IMAGE_NAME . "
    - write: " docker image build -t music-ai . "

- build continer
    
    - EXTEND TO LOCAL NETWORK
        - write: " docker run --rm -d --network=host  IMAGE_NAME:latest  "
        - write: " docker run --rm -d --network=host  music-ai:latest  "
    
    - EXPOSED PORTS
        - write: " docker run -it -p 8080:8080 -d music-ai:latest  "
    
    - ID created with container



[ VSCODE HAS A GREAT DOCKER EXTENTION TO GLANCE AT ENV ]




# Cluster Steps
- MINIKUBE SINGLE-NODE CLUSTER 
    - minikube start
        
    - minikube image load <IMAGE_NAME>

    - minikube image build -t <IMAGE_NAME> .

    - APPLY all config files
        - [image:latest]: ensure docker image has the same name as your desired image 

    - EXPOSE service port:
        - kubectl expose deployment DEPLOYMENT_NAME --type=Loadbalancer --name=SERVICE_NAME

    - CHECK current namespace
        - kubens <NAMESPACE>

     - minikube service struct
        - minikube service <SERVICE_NAME>
        - minikube service list

    - peek single-node enviroment
        - kubect get all
    




- MICROSOFT AZURE
    - ...






- KUBECTX MULTICLUSTER 
    - ...









### Display Container Logs
- docker logs CONTAINER_ID

### Display all Images
- docker images

### Display all Running Containers
- docker container ls

### FREE LOOSE IMAGES & CONTAINERS
- docker system prune