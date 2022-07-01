from .k8s_manage_objects import get_template, deploy_object
from .k8s_database import get_config
from .k8s_client import get_k8s_client
import base64


def build_from_repository(challenge_name, repository):

    challenge_name = challenge_name.replace(" ", "_").lower().strip()

    config = get_config()

    image = 'chal-registry.' + config.https_domain_name + '/' + challenge_name + ':latest'
    
    registry_auth = base64.b64encode(str('ctfd:'+config.registry_password).encode('ascii')).decode('ascii')
    registry_data = base64.b64encode(str('{"auths":{"challenge-registry-service.' + config.registry_namespace + '":{"username":"ctfd","password":"' + config.registry_password + '","auth":"' + registry_auth + '"}' + '}' + '}').encode('ascii')).decode('ascii')

    template = get_template('build')
    options = { 'challenge_name': challenge_name,
                'challenge_repo': repository,
                'registry_namespace': config.registry_namespace,
                'https_domain_name': config.https_domain_name,
                'git_credential': config.git_credential,
                'registry_data': registry_data}

    print("Building challenge...")
    if deploy_object(get_k8s_client(), template, options):
        print("Build succeeded")
    else:
        print("Build failed.")
    
    return image