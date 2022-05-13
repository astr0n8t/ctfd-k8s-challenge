from CTFd.models import db, Challenges
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class

from .k8s_tcp import *
from .k8s_web import *
from .k8s_random_port import *
from ..utils import *

def init_chals(k8s_client):

    result = deploy_registry(k8s_client)
    result = False if not result else deploy_certificates(k8s_client)
    result = False if not result else deploy_web_gateway(k8s_client)

    if result:
        CHALLENGE_CLASSES['k8s-tcp'] = k8sTcpChallengeType
        CHALLENGE_CLASSES['k8s-web'] = k8sWebChallengeType
        CHALLENGE_CLASSES['k8s-random-port'] = k8sRandomPortChallengeType

    return result

def deinit_chals(k8s_client):
    result = destroy_registry(k8s_client)
    result = False if not result else destroy_certificates(k8s_client)
    result = False if not result else destroy_web_gateway(k8s_client)    

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

def deploy_certificates(k8s_client):
    result = False
    registry_template = get_template(4)
    options = { 'tcp_cert_name': 'chal.luctf.dev',
                'istio_namespace': 'istio-system',
                'certificate_issuer_name': 'cloudflare-istio-issuer',
                'tcp_domain_name': 'chal.luctf.dev',
                'https_cert_name': 'web.luctf.dev',
                'https_domain_name': 'web.luctf.dev'}
    if deploy_object(k8s_client, registry_template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed challenge certificates.")
    else:
        print("ctfd-k8s-challenge: Error: deploying challenge certificates failed!")
    return result

def deploy_web_gateway(k8s_client):
    result = False
    registry_template = get_template(5)
    options = { 'istio_namespace': 'istio-system',
                'istio_ingress_name': 'istio-ingressgateway',
                'external_https_port': 443,
                'https_cert_name': 'web.luctf.dev',
                'https_domain_name': 'web.luctf.dev'}
    if deploy_object(k8s_client, registry_template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed web challenge gateway.")
    else:
        print("ctfd-k8s-challenge: Error: deploying web challenge gateway failed!")
    return result

def destroy_registry(k8s_client):
    result = False
    registry_template = get_template(3)
    options = {'registry_namespace': 'registry'}
    if destroy_object(k8s_client, registry_template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: destroying k8s internal challenge registry failed!")
    return result

def destroy_certificates(k8s_client):
    result = False
    registry_template = get_template(4)
    options = { 'tcp_cert_name': 'chal.luctf.dev',
                'istio_namespace': 'istio-system',
                'certificate_issuer_name': 'cloudflare-istio-issuer',
                'tcp_domain_name': 'chal.luctf.dev',
                'https_cert_name': 'web.luctf.dev',
                'https_domain_name': 'web.luctf.dev'}
    if destroy_object(k8s_client, registry_template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed challenge certificates.")
    else:
        print("ctfd-k8s-challenge: Error: destroying challenge certificates failed!")
    return result

def destroy_web_gateway(k8s_client):
    result = False
    registry_template = get_template(5)
    options = { 'istio_namespace': 'istio-system',
                'istio_ingress_name': 'istio-ingressgateway',
                'external_https_port': 443,
                'https_cert_name': 'web.luctf.dev',
                'https_domain_name': 'web.luctf.dev'}
    if destroy_object(k8s_client, registry_template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed web challenge gateway.")
    else:
        print("ctfd-k8s-challenge: Error: destroying web challenge gateway failed!")
    return result
    