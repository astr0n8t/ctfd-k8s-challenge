# pylint: disable=invalid-name
"""
CTFd-K8s-Challenges

This plugin is built to enable CTFd to create
containerized challenge instances using Kubernetes.
It relies on multiple things including Kubernetes,
Istio, and Cert-Manager for it to function correctly.

Written by Nathan Higley <contact@nathanhigley.com>
"""

from CTFd.plugins import register_plugin_assets_directory # pylint: disable=import-error

from .challenges import init_chals, deinit_chals, define_k8s_admin
from .utils import init_db, get_k8s_client, define_k8s_api

def load(app):
    """
    This function is called by CTFd to load the initial plugin.
    """
    app.db.create_all()

    k8s_client = get_k8s_client()
    print("ctfd-k8s-challenge: Successfully loaded Kubernetes config.")

    init_db()
    define_k8s_admin(app)

    if init_chals(k8s_client):
        register_plugin_assets_directory(app, base_path='/plugins/ctfd-k8s-challenge/assets')
        define_k8s_api(app)
    else:
        print(
            "ctfd-k8s-challenge: Error: ctfd-k8s-challenge unable to initialize.  \
                It will be disabled."
            )

    return
