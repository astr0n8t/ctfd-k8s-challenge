# Pulled from https://github.com/kubernetes-client/python/issues/740#issuecomment-1002368049

def get_custom_api() -> CustomObjectsApi:
    global custom_api
    if custom_api is None:
        custom_api = client.CustomObjectsApi(api_client)
    return custom_api


def patch_custom_object_from_yaml(yaml_object: dict, group: str, version: str, namespace: str, name: str, plural: str):
    return get_custom_api().patch_namespaced_custom_object(group,
                                                           version,
                                                           namespace,
                                                           plural,
                                                           name,
                                                           yaml_object)


def create_custom_object_from_yaml(yaml_object: dict, group: str, version: str, namespace: str, plural: str):
    return get_custom_api().create_namespaced_custom_object(group,
                                                            version,
                                                            namespace,
                                                            plural,
                                                            yaml_object)


def apply_custom_object_from_yaml(yaml_object: dict,
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
        exists_obj = get_custom_api().get_namespaced_custom_object(group, version, namespace, plural, name)
        patch_custom_object_from_yaml(yaml_object, group, version, namespace, name, plural)
    except ApiException as e:
        if e.status == 404:
            create_custom_object_from_yaml(yaml_object, group, version, namespace, plural)
        else:
            raise e



