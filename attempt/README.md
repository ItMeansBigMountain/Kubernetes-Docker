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
    - https://learn.microsoft.com/en-us/azure/aks/tutorial-kubernetes-prepare-app

    - CREATE - Image of your container
        - docker image build -t IMAGE_NAME . 

    - CREATE - RG & ACR |  Azure Container Registry
        - az group create -l REGION -n RG_NAME

        -  az acr create --resource-group <myResourceGroup> --name <ContainerRegistryName> --sku Basic

    - LOGIN - into container registry cli & Get Login Server Address 
        -  az acr login --name <ContainerRegistryName>

    - GET SERVER ADDRESS 
        - az acr list --resource-group <myResourceGroup> --query "[].{acrLoginServer:loginServer}" --output table
    
    - CONNECT DESIRED IMAGE VIA DOCKER TAG
        - docker tag <IMAGE_NAME:latest> <acrLoginServer>/<IMAGE_NAME:latest>

    - PUSH NEWLY TAGGED IMAGE TO AZURE
        - docker push <acrLoginServer>/<IMAGE_NAME:latest>

    - DISPLAY IMAGES IN REGISTRY
        - az acr repository list --name <ContainerRegistryName> --output table

    - CREATE KUBERNETES CLUSTER ON AZURE
        - az aks create --resource-group <myResourceGroup> --name <AKS_ClusterName> --node-count 2 --generate-ssh-keys --attach-acr <ContainerRegistryName> 
        
    - INSTALL THE AZURE AKS CLI
        - az aks install-cli
    
    - GET - LOGIN CREDENTIALS TO AKS CLUSTER
        - az aks get-credentials --resource-group <myResourceGroup> --name <AKS_ClusterName>

    - VERIFY - that the nodes are showing on cli
        - kubectl get nodes

    - CREATE KUBERNETE COMPONENT YAML FILES
        -  update kubernetes yaml files image with newly tagged image

        -  kubectl apply -f FILE.yaml
        -  python3 helper.py

    - WATCH SERVICE TO FIND CLUSTER PUBLIC IP ADDRESS
        - kubectl get service azure-vote-front --watch



#### PROJECT STEPS
- az login
- docker image build -t music-ai .
- az group create -l centralus -n demo
- az acr create --resource-group demo --name sosaioyama --sku Basic
- az acr login --name sosaioyama
- az acr list --resource-group demo --query "[].{acrLoginServer:loginServer}" --output table
- docker tag music-ai:latest sosaioyama.azurecr.io/music-ai:v1
- docker push sosaioyama.azurecr.io/music-ai:v1
- az acr repository list --name sosaioyama --output table
- az aks create --resource-group demo --name music-ai-cluster --node-count 2 --generate-ssh-keys --attach-acr sosaioyama
- az aks get-credentials --resource-group demo --name sosaioyama
- az aks get-credentials --resource-group demo --name music-ai-cluster
- kubectl get nodes
- python3 helper.py
- kubens sounddoe
- kubectl get all







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



