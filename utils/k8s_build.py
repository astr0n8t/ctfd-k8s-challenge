from .k8s_manage_objects import get_template, deploy_object
from .k8s_database import get_config
from .k8s_client import get_k8s_client


def build_from_repository(challenge_name, repository):

    challenge_name = challenge_name.replace(" ", "_").lower().strip()

    config = get_config()

    image = 'challenge-registry-service.' + config.registry_namespace + '/' + challenge_name + ':latest'
    
    template = get_template('build')
    options = { 'challenge_name': challenge_name,
                'challenge_repo': repository,
                'registry_namespace': config.registry_namespace,}

    print("Building challenge...")
    if deploy_object(get_k8s_client(), template, options):
        print("Build succeeded")
    else:
        print("Build failed.")
    
    return image