"""
k8s_client

Implements functions that make it easier to get the kubeconfig.
"""
import os
import kubernetes as k8s

def get_k8s_client():
    """
    Gets a normal Kubernetes client.
    """
    if 'KUBERNETES_PORT' in os.environ:
        k8s.config.load_incluster_config()
    else:
        k8s.config.load_kube_config()
    return k8s.client.ApiClient()

def get_k8s_v1_client():
    """
    Gets a v1 Kubernetes client.
    """
    if 'KUBERNETES_PORT' in os.environ:
        k8s.config.load_incluster_config()
    else:
        k8s.config.load_kube_config()
    return k8s.client.CoreV1Api()
