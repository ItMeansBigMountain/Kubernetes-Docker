- Mongo cluster
    - configMap / secrets
    - mongo databse deployment & service (mongodb)
    - mongo databse admin deployment & service (mongo-express)

    - - this allows us to interact with mongoDB within a cluser enviroment
    - - MINICUBE
        - write: ' minikube service SERVICE_NAME '
    


    

# Kubernetes Commands

## install hyperhit and minikube (mac) 
- brew update
- brew install hyperkit
- brew install minikube
- kubectl
- minikube

## create minikube cluster
- minikube start --vm-driver=hyperkit
- kubectl get nodes
- minikube status
- kubectl version

## delete cluster and restart in debug mode
- minikube delete
- minikube start --vm-driver=hyperkit --v=7 --alsologtostderr
- minikube status

## kubectl commands
- kubectl get nodes
- kubectl get pod
- kubectl get services
- kubectl create deployment nginx-depl --image=nginx
- kubectl get deployment
- kubectl get replicaset
- kubectl edit deployment nginx-depl

## debugging
- kubectl logs {pod-name}
- kubectl exec -it {pod-name} -- bin/bash

## create mongo deployment
- kubectl create deployment mongo-depl --image=mongo
- kubectl logs mongo-depl-{pod-name}
- kubectl describe pod mongo-depl-{pod-name}

## delete deplyoment
- kubectl delete deployment mongo-depl
- kubectl delete deployment nginx-depl

## create or edit config file
- vim nginx-deployment.yaml
- kubectl apply -f nginx-deployment.yaml
- kubectl get pod
- kubectl get deployment

## delete with config
- kubectl delete -f nginx-deployment.yaml


## Metrics
- kubectl top:  The kubectl top command returns current CPU and memory usage for a cluster’s pods or nodes, or for a particular pod or node if specified.





# CONFIGURATION FILES
- There are multiple config files 
    - each component needs a config file

## yaml sections
- Kind (type of component)
- Metadata
    - name
    - labels
- Spec
    - replicas (load balance)
    - selector (app label)
    - Templates (pods)
        spec (each pod container has specs for its vm)
            - port config





## secrets.yaml
- VALUES MUST BE BASE 64 ENCODED
    - write: 'echo -n "secret string" | base64'
    - paste that output into secrets.yaml key pair, value




## setting up service.yaml
- Internal
    - no need to identify type
    - match the ports of container and service

- External
    - identify type as LoadBalancer
    
    - MINICUBE
        - minikube service SERVICE_NAME


