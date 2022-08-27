"""
k8s_manage_custom_resources

Pulled from GitHub to manage custom resources efficiently.
"""
# Pulled from https://github.com/kubernetes-client/python/issues/740#issuecomment-1002368049
import kubernetes as k8s
def get_custom_api(api_client) ->  k8s.client.CustomObjectsApi:
    """
    Returns a custom objects api for k8s.
    """
    return k8s.client.CustomObjectsApi(api_client)


def patch_custom_object_from_yaml(api_client, yaml_object: dict, #pylint: disable=too-many-arguments
                                  group: str, version: str, namespace: str,
                                  name: str, plural: str):
    """
    Patches a custom object using a yaml definition.
    """
    return get_custom_api(api_client).patch_namespaced_custom_object(group,
                                                           version,
                                                           namespace,
                                                           plural,
                                                           name,
                                                           yaml_object)


def create_custom_object_from_yaml(api_client, yaml_object: dict, #pylint: disable=too-many-arguments
                                   group: str, version: str, namespace: str,
                                plural: str):
    """
    Creates a custom object using a yaml definition.
    """
    return get_custom_api(api_client).create_namespaced_custom_object(group,
                                                            version,
                                                            namespace,
                                                            plural,
                                                            yaml_object)


def apply_custom_object_from_yaml(api_client, yaml_object: dict, #pylint: disable=too-many-arguments
                                  group: str = None,
                                  version: str = None,
                                  namespace: str = None,
                                  name: str = None,
                                  plural: str = None):
    """
    Actually applies a custom object from yaml.
    """
    if not name:
        name = yaml_object['metadata']['name']
    if not group or not version:
        api_version = yaml_object['apiVersion']
        group = api_version[0: api_version.find('/')]
        version = api_version[api_version.find('/') + 1:]
    if not namespace:
        namespace = yaml_object['metadata']['namespace']
    if not plural:
        plural = yaml_object['kind'].lower() + 's'
    try:
        get_custom_api(api_client).get_namespaced_custom_object(group,
                                        version, namespace, plural, name)
        patch_custom_object_from_yaml(api_client, yaml_object, group,
                                        version, namespace, name, plural)
    except k8s.client.rest.ApiException as general_exception:
        if general_exception.status == 404:
            create_custom_object_from_yaml(api_client, yaml_object, group,
                                                version, namespace, plural)
        else:
            print("ERROR: ctfd-k8s-challenges: ", general_exception)

def delete_custom_object_from_yaml(api_client, yaml_object: dict, #pylint: disable=too-many-arguments
                                  group: str = None,
                                  version: str = None,
                                  namespace: str = None,
                                  name: str = None,
                                  plural: str = None):
    """
    Deletes a custom object from yaml.
    """
    if not name:
        name = yaml_object['metadata']['name']
    if not group or not version:
        api_version = yaml_object['apiVersion']
        group = api_version[0: api_version.find('/')]
        version = api_version[api_version.find('/') + 1:]
    if not namespace:
        namespace = yaml_object['metadata']['namespace']
    if not plural:
        plural = yaml_object['kind'].lower() + 's'
    try:
        get_custom_api(api_client).get_namespaced_custom_object(group, version,
                                                        namespace, plural, name)
        get_custom_api(api_client).delete_namespaced_custom_object(group, version,
                                                        namespace, plural, name)
    except k8s.client.rest.ApiException as general_exception:
        print("ERROR: ctfd-k8s-challenges: ", general_exception)
