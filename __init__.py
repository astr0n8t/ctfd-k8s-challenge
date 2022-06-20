from .challenges import init_chals, deinit_chals, define_k8s_admin
from .utils import init_db, get_k8s_client

from CTFd.plugins import register_plugin_assets_directory

def load(app):
    app.db.create_all()

    k8s_client = get_k8s_client()
    print("ctfd-k8s-challenge: Successfully loaded Kubernetes config.")

    init_db()

    if init_chals(k8s_client):
        register_plugin_assets_directory(app, base_path='/plugins/ctfd-k8s-challenge/assets')
        define_k8s_admin(app)
    else:
        print("ctfd-k8s-challenge: Error: ctfd-k8s-challenge unable to initialize.  It will be disabled.")

    return