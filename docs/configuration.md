# Configuration

This plugin assumes that it can load a kubeconfig that allows it to perform various tasks within the cluster.

You have two choices with how to deploy this plugin:

## Deploy CTFd in Kubernetes

This is probably the easiest way to do this.  Deploy CTFd as a container in the Kubernetes cluster that you want to spin up challenge pods in.  The only drawback is if you're concerned about security with the challenge pods being in the same cluster as CTF infrastructure.  I'll leave that decision up to you.

In order to do this, you just need to give the k8s pod a dedicated service account in the cluster and bind some permissions to it.  [See this rbac example for what it needs.](examples/rbac.yaml)  The rbac example should have the least amount of privileges that the CTFd pod would need to do it's job.

If you spin up Kubernetes in this manner, then the plugin will auto-detect the kubeconfig and you're done as far as it accessing the cluster. You can skip to the section on the config.

## Deploy CTFd elsewhere

In this case, you need to give the CTFd instance access to a kubeconfig with the permissions for a Kubernetes cluster where you would like to deploy challenge instances.  I still recommend utilizing [the rbac example](examples/rbac.yaml) for creating a service account.

The actual code that grabs the kubeconfig will use the `kubernetes.config.load_kube_config()` function but should pull from `~/.kube/config` for the user that CTFd runs as.

Make sure CTFd can access the cluster and has permissions and you should be good to go.

## Config.yaml

The YAML config is where the actual configuration for the plugin is specified.

The special keyword `env` can be used on some keys to have the plugin pull from the system environment variable rather than need it be specified in the config.

Each option is listed here with a description:

| Key | Description | Default | Environment Variable |
|-----------------|-------------------------------------------------|-----------------------|--------------|
| git_username | The username for git to use when pulling challenge repositories that contain Dockerfiles | env | K8S_CHALLENGES_GIT_USER |
| git_credential | The password (or token) for git to use when pulling challenge repositories that contain Dockerfiles | env | K8S_CHALLENGES_GIT_CREDENTIAL | 
| registry_password | The password for the Docker registry to use (used both for internal docker registry and as image pull secrets) | env | K8S_CHALLENGES_REGISTRY_PASSWORD |
| registry_namespace | The namespace to deploy the internal Docker registry to | registry | N/A |
| challenge_namespace | The namepscae to deploy challenge instances to | challenges | N/A |
| istio_namespace | The namespace where istio lives | istio-system | N/A |
| tcp_domain_name | The wildcard DNS record that will be used to generate TCP challenge instance URLs (should point to the istio ingress IP) | chal.example.com | N/A |
| https_domain_name | The wildcard DNS record that will be used to generate HTTPS challenge instance URLs (should point to the istio ingress IP) | web.example.com | N/A |
| certificate_issuer_name | The name of the cert-manager cluster issuer to use to generate TLS certificates for Istio (will be wildcard certificates based on `*_domain_name` variables) | istio-issuer | N/A |
| istio_ingress_name | The name of the Istio ingress that challenge's will be routed through (the wildcard DNS records should point to this ingress's external IP) | ingressgateway | N/A |
| external_tcp_port | The external port of the ingress gateway to use for TCP challenges (should be fine to leave as 443) | 443 | N/A |
| external_https_port | The external port of the ingress gateway to use for https challenges (should be fine to leave as 443) | 443 | N/A |
| expire_interval | Time in seconds that challenges should be alive for (user's have option to extend after half the time has expired) | 3600 (an hour) | N/A |
| ctfd_url | The URL that the plugin can access CTFd at (needed for expiration of challenges due to how flask works) | http://ctfd-service.ctfd | N/A |

