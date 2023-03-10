"""
challenges

This module implements the actual challenge types of the plugins.
"""
import re
import uuid
import hashlib
import bcrypt
from CTFd.models import db, Challenges                                               # pylint: disable=import-error
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class # pylint: disable=import-error

from .k8s_tcp import *
from .k8s_web import *
from .k8s_random_port import *
from .k8s_admin import define_k8s_admin
from ..utils import *

def init_chals(k8s_client):
    """
    Initializes resources for the challenge types.
    Also registers the actual challenge classes.
    """
    config = get_config()

    if not config.challenge_namespace:
        return False

    result = deploy_certificates(k8s_client, config)
    result = False if not result else deploy_web_gateway(k8s_client, config)
    result = False if not result else deploy_registry(k8s_client, config)
    result = False if not result else deploy_cleanup_cronjob(k8s_client, config)

    if result:
        CHALLENGE_CLASSES['k8s-tcp'] = K8sTcpChallengeType
        CHALLENGE_CLASSES['k8s-web'] = K8sWebChallengeType
        CHALLENGE_CLASSES['k8s-random-port'] = K8sRandomPortChallengeType

    return result

def deinit_chals(k8s_client):
    """
    Removes challenge resources.

    Currently unused.
    """

    config = get_config()

    result = destroy_certificates(k8s_client, config)
    result = False if not result else destroy_cleanup_cronjob(k8s_client, config)
    result = False if not result else destroy_web_gateway(k8s_client, config)
    result = False if not result else destroy_registry(k8s_client, config)

    return result

def deploy_registry(k8s_client, config):
    """
    Deploys the internal challenge registry in Kubernetes.
    """

    def encrypt_password(username, password):
        """
        Quick function to return a htpasswd formatted hash of password.
        """

        bcrypted = bcrypt.hashpw(password.encode("utf-8"),
                                bcrypt.gensalt(rounds=12)).decode("utf-8")
        bcrypted = re.sub(r"\$2[^a]\$", "$2y$", bcrypted)
        return f"{username}:{bcrypted}"

    result = False
    template = get_template('registry')

    if not config.registry_password:
        config.registry_password = str(hashlib.md5(bytes(str(uuid.uuid4()), 'utf-8')).hexdigest())
        db.session.commit()

    registry_hash = encrypt_password('ctfd', config.registry_password)

    options = {'registry_namespace': config.registry_namespace,
               'istio_namespace': config.istio_namespace,
               'https_domain_name': config.https_domain_name,
               'registry_hash': registry_hash}

    if deploy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: deploying k8s internal challenge registry failed!")
    return result

def deploy_certificates(k8s_client, config):
    """
    Deploys the certificates for the challenge endpoints.
    """

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
    """
    Deploys the Istio Gateway for the web challenges.
    """

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

def deploy_cleanup_cronjob(k8s_client, config):
    """
    Deploys the cronjob which calls the /api/v1/k8s/clean endpoint every minute.
    """

    result = False
    template = get_template('clean')
    options = {'ctfd_url': config.ctfd_url,
               'challenge_namespace': config.challenge_namespace}
    if deploy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed cleanup cronjob.")
    else:
        print("ctfd-k8s-challenge: Error: deploying cleanup cronjob failed!")
    return result

def destroy_registry(k8s_client, config):
    """
    Destroys the registry deployment from Kubernetes.
    """

    result = False
    template = get_template('registry')
    options = {'registry_namespace': config.registry_namespace}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: destroying k8s internal challenge registry failed!")
    return result

def destroy_certificates(k8s_client, config):
    """
    Destroys the certificates from Kubernetes.
    """

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

def destroy_web_gateway(k8s_client, config):
    """
    Destroys the Istio Gateway from Kubernetes.
    """

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

def destroy_cleanup_cronjob(k8s_client, config):
    """
    Destroys the cleanup cronjob.
    """

    result = False
    template = get_template('clean')
    options = {'ctfd_url': config.ctfd_url,
               'challenge_namespace': config.challenge_namespace}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed cleanup cronjob.")
    else:
        print("ctfd-k8s-challenge: Error: destroying cleanup cronjob failed!")
    return result
