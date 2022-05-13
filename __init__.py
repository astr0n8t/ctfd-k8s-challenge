from .challenges import init_chals

from CTFd.plugins import register_plugin_assets_directory

import kubernetes as k8s
import os

def load(app):
    app.db.create_all()

    k8s_client = get_k8s_client()
    print("ctfd-k8s-challenge: Successfully loaded Kubernetes config.")

    if init_chals(k8s_client):
        register_plugin_assets_directory(app, base_path='/plugins/ctfd-k8s-challenge/assets')
    else:
        print("ctfd-k8s-challenge: Error: ctfd-k8s-challenge unable to initialize.  It will be disabled.")
    return

def get_k8s_client():
    if 'KUBERNETES_PORT' in os.environ:
        k8s.config.load_incluster_config()
    else:
        k8s.config.load_kube_config()
    k8s.client.CustomObjectsApi().list_cluster_custom_object(group="cert-manager.io", version="v1", plural="Certificates")
    return k8s.client.ApiClient()