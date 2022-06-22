import kubernetes as k8s
from .k8s_delete_from_yaml import delete_from_yaml
from .k8s_manage_custom_resources import apply_custom_object_from_yaml, delete_custom_object_from_yaml
import yaml
from jinja2 import Template

def get_template(template_name):
    # template_types = ['k8s-tcp', 'k8s-web', 'k8s-random-port', 'registry', 'certificates', 'web-gateway', 'build']
    
    template_path = 'CTFd/plugins/ctfd-k8s-challenge/templates/' + template_name + '.yml.j2'

    template = ''

    with open(template_path) as f:
        template = f.read()

    return Template(template)
    

def deploy_object(k8s_client, template, template_variables):

    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    for yaml_file in dep:
        api_name = yaml_file['apiVersion'] 
        kind = yaml_file['kind']

        if 'cert-manager' in api_name or 'istio' in api_name or kind == 'Job':
            apply_custom_object_from_yaml(k8s_client, yaml_file)
        else:
            try:
                k8s.utils.create_from_yaml(k8s_client, yaml_objects=[yaml_file])
            except Exception as e:
                if not '"reason":"AlreadyExists"' in str(e):
                    result = False
                    print(e)

    return result


def destroy_object(k8s_client, template, template_variables):

    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    for yaml_file in dep:
        api_name = yaml_file['apiVersion'] 
        kind = yaml_file['kind']

        if 'cert-manager' in api_name or 'istio' in api_name or kind == 'Job':
            delete_custom_object_from_yaml(k8s_client, yaml_file)
        else:
            try:
                delete_from_yaml(k8s_client, yaml_objects=[yaml_file])
            except Exception as e:
                result = False
                print(e)
    return result

def get_registry_password(k8s_client, config):
    password = ""

    while not password:
        try:
            pod_name = ""
            pod_list = k8s_client.list_namespaced_pod(config.registry_namespace).items
            for pod in pod_list:
                if 'registry' in pod.metadata.name:
                    pod_name = pod.metadata.name
            logs = str(k8s_client.read_namespaced_pod_log(
                name=pod_name,
                namespace=config.registry_namespace,
                container="registry"))
            if "msg=\"htpasswd is missing, provisioning with default user\"" in logs:
                password = logs.split("password=")[1].split(" user=docker")[0]
        except Exception as e:
            pass

    return password