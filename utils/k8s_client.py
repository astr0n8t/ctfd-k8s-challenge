import kubernetes as k8s
import os

def get_k8s_client():
    if 'KUBERNETES_PORT' in os.environ:
        k8s.config.load_incluster_config()
    else:
        k8s.config.load_kube_config()
    return k8s.client.ApiClient()