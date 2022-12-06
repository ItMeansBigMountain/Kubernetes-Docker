# MINIKUBE CLUSTER

- BUILD DOCKER IMAGE
    - cd into project and build docker image
        - docker image build -t <IMAGE_NAME> . 
    
    [DELETE]: ensure image runs right using it as a container 
    - docker run -it -p 8080:8080 -d <IMAGE_NAME:latest>
    - docker logs <IMAGE_ID>
    - docker stop  <CONTAINER_ID>
    - docker rm  <CONTAINER_ID>


- MINIKUBE SINGLE CLUSTER 
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
    




# MICROSOFT AZURE
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
- az aks get-credentials --resource-group demo --name music-ai-cluster
- kubectl get nodes
- python3 helper.py
- kubens sounddoe
- kubectl get all


