"""
k8s_random_port

Defines the challenge type for random port challenges.
"""
from flask import Blueprint # pylint: disable=import-error
from .k8s_challenge import K8sChallengeType

class K8sRandomPortChallengeType(K8sChallengeType):
    """
    The challenge type for random port challenges.
    """
    id = "k8s-random-port"
    name = "k8s-random-port"
    templates = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/create.html',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/update.html',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/view.html',
    }
    scripts = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/create.js',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/update.js',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/view.js',
    }
    route = '/plugins/ctfd-k8s-challenge/assets/k8s_random_port'
    blueprint = Blueprint('ctfd-k8s-challenge', __name__,
                            template_folder='templates', static_folder='assets')
