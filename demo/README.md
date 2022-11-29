## Runs a cluster hosting two pods
- Database container
- DB Admin GUI container


### side notes
- may have to inspect and change webapps css display from none to block
- kubectl logs webapp-deployment-xxx-xxx 
    - should display "app listening on port 3000!"
- make sure to start service on minikube
    - minikube service SERVICE_NAME
