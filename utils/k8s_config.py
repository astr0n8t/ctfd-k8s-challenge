"""
k8s_config

Reads the config file.
"""
import os
import yaml

def read_config_file():
    """
    Reads the config file and environment variables.
    """

    config_file_path =  'CTFd/plugins/ctfd-k8s-challenge/config'

    if os.path.exists(str(config_file_path + '.yaml')):
        config_file_path += '.yaml'
    elif os.path.exists(str(config_file_path + '.yml')):
        config_file_path += '.yml'
    else:
        return False

    with open(config_file_path, encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)

    if 'git_credential' in config and config['git_credential'] == 'env':
        config['git_credential'] = os.getenv('K8S_CHALLENGES_GIT_CREDENTIAL')
    if 'git_user' in config and config['git_user'] == 'env':
        config['git_user'] = os.getenv('K8S_CHALLENGES_GIT_USER')
    if 'registry_password' in config and config['registry_password'] == 'env':
        config['registry_password'] = os.getenv('K8S_CHALLENGES_REGISTRY_PASSWORD')

    return config
