# Pulled from https://github.com/kubernetes-client/python/issues/740#issuecomment-1002368049
import kubernetes as k8s
def get_custom_api(api_client) ->  k8s.client.CustomObjectsApi:
    return k8s.client.CustomObjectsApi(api_client)


def patch_custom_object_from_yaml(api_client, yaml_object: dict, group: str, version: str, namespace: str, name: str, plural: str):
    return get_custom_api(api_client).patch_namespaced_custom_object(group,
                                                           version,
                                                           namespace,
                                                           plural,
                                                           name,
                                                           yaml_object)


def create_custom_object_from_yaml(api_client, yaml_object: dict, group: str, version: str, namespace: str, plural: str):
    return get_custom_api(api_client).create_namespaced_custom_object(group,
                                                            version,
                                                            namespace,
                                                            plural,
                                                            yaml_object)


def apply_custom_object_from_yaml(api_client, yaml_object: dict,
                                  group: str = None,
                                  version: str = None,
                                  namespace: str = None,
                                  name: str = None,
                                  plural: str = None):
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
        exists_obj = get_custom_api(api_client).get_namespaced_custom_object(group, version, namespace, plural, name)
        patch_custom_object_from_yaml(api_client, yaml_object, group, version, namespace, name, plural)
    except k8s.client.rest.ApiException as e:
        if e.status == 404:
            create_custom_object_from_yaml(api_client, yaml_object, group, version, namespace, plural)
        else:
            raise e

def delete_custom_object_from_yaml(api_client, yaml_object: dict,
                                  group: str = None,
                                  version: str = None,
                                  namespace: str = None,
                                  name: str = None,
                                  plural: str = None):
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
        exists_obj = get_custom_api(api_client).get_namespaced_custom_object(group, version, namespace, plural, name)
        get_custom_api(api_client).delete_namespaced_custom_object(group, version, namespace, plural, name)
    except k8s.client.rest.ApiException as e:
        if e.status != 404:
            print(e)



