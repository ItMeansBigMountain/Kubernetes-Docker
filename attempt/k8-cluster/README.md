# MINIKUBE CLUSTER

- BUILD DOCKER IMAGE
    - cd into project and build docker image
        - docker image build -t <IMAGE_NAME> . 
    
    [DELETE]: ensure image runs right using it as a container 
    - docker run --rm -d --network=host  <IMAGE_NAME:latest>
    - docker logs <IMAGE_ID>
    - docker stop  <CONTAINER_ID>
    - docker rm  <CONTAINER_ID>


- MINIKUBE SINGLE CLUSTER 
    - minikube start
        
    - minikube image load <IMAGE_NAME>

    - minikube image build -t <IMAGE_NAME> .

    - apply all config files
        - [image:latest]: ensure docker image has the same name as your desired image 

    - current namespace
        - kubens <NAMESPACE>

     - minikube service struct
        - minikube service <SERVICE_NAME>

    - peek single-node enviroment
        - kubect get all
    




- MICROSOFT AZURE
    - ...



- KUBECTX MULTICLUSTER 
    - ...