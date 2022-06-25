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