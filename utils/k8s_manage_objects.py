import kubernetes as k8s
from .k8s_delete_from_yaml import delete_from_yaml
import yaml
from jinja2 import Template

def get_template(template_id):
    template_types = ['k8s-tcp', 'k8s-web', 'k8s-random-port', 'registry']
    
    template_path = 'CTFd/plugins/ctfd-k8s-challenge/templates/' + template_types[template_id] + '.yml.j2'

    template = ''

    with open(template_path) as f:
        template = f.read()

    return Template(template)
    

def deploy_object(k8s_client, template, template_variables):

    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    try:
        k8s.utils.create_from_yaml(k8s_client, yaml_objects=dep)
    except Exception as e:
        if not '"reason":"AlreadyExists"' in str(e):
            result = False
            print(e)

    return result


def destroy_object(k8s_client, template, template_variables):

    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    try:
        delete_from_yaml(k8s_client, yaml_objects=dep)
    except Exception as e:
        result = False

    return result