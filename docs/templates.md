# Templates

The templates folder contains various YAML templates that the plugin will use to build various items.  You can change these templates to affect how the plugin deploys things into the k8s cluster.

## Example: Bring your own Registry

As an example, if you wanted to bring your own registry, you would replace the `registry.yml.j2` file with something like
```yaml
apiVersion: v1
kind: Service
metadata:
  name: challenge-registry-service
  namespace: {{ registry_namespace }}
spec:
  selector:
    app: registry
  type: ExternalName
  externalName: my.database.example.com
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: registry-vs
  namespace: {{ registry_namespace }}
spec:
  hosts:
  - "chal-registry.{{ https_domain_name }}"
  gateways:
  - {{ istio_namespace }}/k8s-https-challenge-gateway
  http:
  - route:
    - destination:
        host: challenge-registry-service
        port:
          number: 443 
```

And then you could even extend this by building the images ahead of time just making sure that the images are named the name of the challenge in lowercase with all spaces replaced by hyphens.

Replace `build.yml.j2` with just this:
```
apiVersion: v1
kind: Secret
metadata:
  name: registry-auth-map
  namespace: {{ registry_namespace }}
data:
  .dockerconfigjson: {{ registry_data }}
```

Or you can manually deploy the secret, or change the template for the actual containers.

## Full Template Reference

### build

Deployed everytime a new challenge of one of the three plugin types is created.  It's purpose is as a build stage of the Git repository fed into the challenge configuration

#### Templated Variables

| Name | Value |
|--------------|----------------------------|
| challenge_name | The name of the challenge (all lowercase, with spaces replaced by hyphens) |
| registry_namespace | The namespace the registry is deployed into |
| challenge_repo | The URL of the source git repository specified for the challenge |
| registry_data | The base64 encoded docker config for image pull secrets to pull from the registry |
| git_user | The username of the account used to authenticate to the challenge_repo |
| git_credential | The password/token of the account used to authenticate to the challenge_repo |

### certificates

Used to provision certificates for the challenge ingress's.

#### Templated Variables

| Name | Value |
|--------------|----------------------------|
| tcp_cert_name | The name of the certificate resource to be deployed |
| istio_namespace | The namespace that Istio is deployed to |
| certificate_issuer_name | The cert-manager issuer specified in the config file |
| tcp_domain_name | The domain name for TCP challenge types specified in the config file |
| https_domain_name | The domain name for https challenge types specified in the config file |

### clean

Used to deploy a cronjob that curls the clean endpoint every minute.  It is needed for automatic expiration of challenge instances.

#### Templated Variables

| Name | Value |
|--------------|----------------------------|
| challenge_namespace | The namespace that challenges will be deployed to |
| ctfd_url | The URL that it will access the CTFd instance at |

### k8s-random-port

Used for on demand challenge instances of type random port.  Deployed everytime a user requests an instance.

| Name | Value |
|--------------|----------------------------|
| deployment_name | The name of the deployment, a unique uuid appended to the 'chal-' prefix |
| challenge_namespace | The namespace that challenges will be deployed to |
| container_name | The container image that will be deployed, expects to be of form 'challenge_name' with tag 'latest' |
| challenge_port | The port specified when creating the challenge that the container listens on |
| registry_data | The base64 encoded docker config for image pull secrets to pull from the registry |
| random_port | A random port generated between 40000 and 50000 that the instance will be externally accessible via |
| istio_namespace | The namespace that Istio is deployed to |
| istio_ingress_name | The name of the Istio ingress that will be used to allow access to the instance |

### k8s-tcp

Used for on demand challenge instances of type TCP/TLS.  Deployed everytime a user requests an instance.

| Name | Value |
|--------------|----------------------------|
| deployment_name | The name of the deployment, a unique uuid appended to the 'chal-' prefix |
| challenge_namespace | The namespace that challenges will be deployed to |
| container_name | The container image that will be deployed, expects to be of form 'challenge_name' with tag 'latest' |
| challenge_port | The port specified when creating the challenge that the container listens on |
| registry_data | The base64 encoded docker config for image pull secrets to pull from the registry |
| external_tcp_port | The TCP port specified in the config for TCP challenges, typically 443 |
| tcp_cert_name | The name of the certificate resource that CTFd deployed |
| tcp_domain_name | The domain name specified in the config for TCP challenges |
| istio_namespace | The namespace that Istio is deployed to |
| istio_ingress_name | The name of the Istio ingress that will be used to allow access to the instance |

### k8s-web

Used for on demand challenge instances of type TCP/TLS.  Deployed everytime a user requests an instance.

| Name | Value |
|--------------|----------------------------|
| deployment_name | The name of the deployment, a unique uuid appended to the 'chal-' prefix |
| challenge_namespace | The namespace that challenges will be deployed to |
| container_name | The container image that will be deployed, expects to be of form 'challenge_name' with tag 'latest' |
| challenge_port | The port specified when creating the challenge that the container listens on |
| registry_data | The base64 encoded docker config for image pull secrets to pull from the registry |
| https_domain_name | The domain name specified in the config for https challenges |
| istio_namespace | The namespace that Istio is deployed to |

### registry

Used to deploy an internal container registry to store challenge container images.

| Name | Value |
|--------------|----------------------------|
| registry_namespace | The namespace the registry is deployed into |
| registry_hash | The bcrypt hash of the registry password |
| https_domain_name | The domain name specified in the config for https challenges |
| istio_namespace | The namespace that Istio is deployed to |

### web-gateway

Used to deploy the Istio gateway for https challenges and registry.  A weird quirk of how Istio handles web traffic requires us to handle web challenges like this.

| Name | Value |
|--------------|----------------------------|
| istio_namespace | The namespace that Istio is deployed to |
| istio_ingress_name | The name of the Istio ingress that will be used to allow access to the instance |
| external_https_port | The TCP port specified in the config for https challenges, typically 443 |
| https_cert_name | The name of the certificate resource that CTFd deployed |
| https_domain_name | The domain name specified in the config for https challenges |

