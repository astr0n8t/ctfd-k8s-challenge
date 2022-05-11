from CTFd.models import db, Challenges
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class

from .k8s_tcp import *
from .k8s_web import *
from .k8s_random_port import *

def init_chals():
    CHALLENGE_CLASSES['k8s-tcp'] = k8sTcpChallengeType
    CHALLENGE_CLASSES['k8s-web'] = k8sWebChallengeType
    CHALLENGE_CLASSES['k8s-random-port'] = k8sRandomPortChallengeType
    
    