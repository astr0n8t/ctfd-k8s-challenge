"""
k8s_tcp

Defines the challenge type for tcp challenges.
"""
from flask import Blueprint # pylint: disable=import-error
from .k8s_challenge import K8sChallengeType

class K8sTcpChallengeType(K8sChallengeType):
    """
    The challenge type for tcp challenges.
    """
    id = "k8s-tcp"
    name = "k8s-tcp"
    templates = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/create.html',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/update.html',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/view.html',
    }
    scripts = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/create.js',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/update.js',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/view.js',
    }
    route = '/plugins/ctfd-k8s-challenge/assets/k8s_tcp'
    blueprint = Blueprint('ctfd-k8s-challenge', __name__,
                            template_folder='templates', static_folder='assets')
