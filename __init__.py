from .challenges import init_chals

from CTFd.plugins import register_plugin_assets_directory

def load(app):
    app.db.create_all()
    init_chals()
    register_plugin_assets_directory(app, base_path='/plugins/ctfd-k8s-challenge/assets')
    return