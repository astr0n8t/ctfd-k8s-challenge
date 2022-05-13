from CTFd.models import db, Challenges
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class

from .k8s_tcp import *
from .k8s_web import *
from .k8s_random_port import *
from ..utils import *

def init_chals(k8s_client):
    result = True
    if deploy_registry(k8s_client):
        CHALLENGE_CLASSES['k8s-tcp'] = k8sTcpChallengeType
        CHALLENGE_CLASSES['k8s-web'] = k8sWebChallengeType
        CHALLENGE_CLASSES['k8s-random-port'] = k8sRandomPortChallengeType
    else:
        result = False
    return result
    

def deploy_registry(k8s_client):
    result = False
    registry_template = get_template(3)
    options = {'registry_namespace': 'registry'}
    if deploy_object(k8s_client, registry_template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: deploying k8s internal challenge registry failed!")
    return result