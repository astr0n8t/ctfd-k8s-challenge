from CTFd.models import db, Challenges
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class

from .k8s_tcp import *
from .k8s_web import *
from .k8s_random_port import *
from .k8s_config import define_k8s_admin
from ..utils import *

def init_chals(k8s_client):

    config = get_config()
    result = deploy_registry(k8s_client, config)
    result = False if not result else deploy_certificates(k8s_client, config)
    result = False if not result else deploy_web_gateway(k8s_client, config)

    if result:
        CHALLENGE_CLASSES['k8s-tcp'] = k8sTcpChallengeType
        CHALLENGE_CLASSES['k8s-web'] = k8sWebChallengeType
        CHALLENGE_CLASSES['k8s-random-port'] = k8sRandomPortChallengeType

    return result

def deinit_chals(k8s_client):
    config = get_config()
    result = destroy_registry(k8s_client, config)
    result = False if not result else destroy_certificates(k8s_client, config)
    result = False if not result else destroy_web_gateway(k8s_client, config)    

    return result

def deploy_registry(k8s_client, config):
    result = False
    template = get_template('registry')
    options = {'registry_namespace': config.registry_namespace}
    if deploy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: deploying k8s internal challenge registry failed!")
    return result

def deploy_certificates(k8s_client, config):
    result = False
    template = get_template('certificates')
    options = { 'tcp_cert_name': config.tcp_domain_name,
                'istio_namespace': config.istio_namespace,
                'certificate_issuer_name': config.certificate_issuer_name,
                'tcp_domain_name': config.tcp_domain_name,
                'https_cert_name': config.https_domain_name,
                'https_domain_name': config.https_domain_name}
    if deploy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed challenge certificates.")
    else:
        print("ctfd-k8s-challenge: Error: deploying challenge certificates failed!")
    return result

def deploy_web_gateway(k8s_client, config):
    result = False
    template = get_template('web-gateway')
    options = { 'istio_namespace': config.istio_namespace,
                'istio_ingress_name': config.istio_ingress_name,
                'external_https_port': config.external_https_port,
                'https_cert_name': config.https_domain_name,
                'https_domain_name': config.https_domain_name}
    if deploy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed web challenge gateway.")
    else:
        print("ctfd-k8s-challenge: Error: deploying web challenge gateway failed!")
    return result

def destroy_registry(k8s_client, config):
    result = False
    template = get_template('registry')
    options = {'registry_namespace': config.registry_namespace}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: destroying k8s internal challenge registry failed!")
    return result

def destroy_certificates(k8s_client):
    result = False
    template = get_template('certificates')
    options = { 'tcp_cert_name': config.tcp_domain_name,
                'istio_namespace': config.istio_namespace,
                'certificate_issuer_name': config.certificate_issuer_name,
                'tcp_domain_name': config.tcp_domain_name,
                'https_cert_name': config.https_domain_name,
                'https_domain_name': config.https_domain_name}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed challenge certificates.")
    else:
        print("ctfd-k8s-challenge: Error: destroying challenge certificates failed!")
    return result

def destroy_web_gateway(k8s_client):
    result = False
    template = get_template('web-gateway')
    options = { 'istio_namespace': config.istio_namespace,
                'istio_ingress_name': config.istio_ingress_name,
                'external_https_port': config.external_https_port,
                'https_cert_name': config.https_domain_name,
                'https_domain_name': config.https_domain_name}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed web challenge gateway.")
    else:
        print("ctfd-k8s-challenge: Error: destroying web challenge gateway failed!")
    return result
    