from .challenges import init_chals, deinit_chals
from .utils import init_db

from CTFd.plugins import register_plugin_assets_directory

import kubernetes as k8s
import os

def load(app):
    app.db.create_all()

    k8s_client = get_k8s_client()
    print("ctfd-k8s-challenge: Successfully loaded Kubernetes config.")

    init_db()

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
    return k8s.client.ApiClient()