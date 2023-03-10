"""
k8s_build

Defines how challenge container images are built and stored in the registry.
"""

import base64

from .k8s_manage_objects import get_template, deploy_object
from .k8s_database import get_config
from .k8s_client import get_k8s_client



def build_from_repository(challenge_name, repository):
    """
    Builds a challenge from a git repository and pushes it to the internal registry.
    """
    challenge_name = challenge_name.replace(" ", "-").lower().strip()

    config = get_config()

    image = 'chal-registry.' + config.https_domain_name + '/' + challenge_name + ':latest'

    registry_auth = base64.b64encode(str('ctfd:'+
                                        config.registry_password).encode('ascii')).decode('ascii')
    registry_data = base64.b64encode(str('{"auths":{"challenge-registry-service.' +
                                            config.registry_namespace +
                                            '":{"username":"ctfd","password":"' +
                                            config.registry_password +
                                            '","auth":"' +
                                            registry_auth + '"}' + '}' +
                                            '}').encode('ascii')).decode('ascii')

    git_user = base64.b64encode(str(config.git_user).encode('ascii')).decode('ascii')
    git_password = base64.b64encode(str(config.git_credential).encode('ascii')).decode('ascii')

    template = get_template('build')
    options = { 'challenge_name': challenge_name,
                'challenge_repo': repository,
                'registry_namespace': config.registry_namespace,
                'https_domain_name': config.https_domain_name,
                'git_credential': git_password,
                'git_user': git_user,
                'registry_data': registry_data}

    print("Building challenge...")
    if deploy_object(get_k8s_client(), template, options):
        print("Build succeeded")
    else:
        print("Build failed.")

    return image
