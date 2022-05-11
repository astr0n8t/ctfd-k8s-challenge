import kubernetes as k8s
import k8s_delete_from_yaml
import yaml
from jinja2 import Template

def get_template(chal_type):
    challenge_types = ['k8s-tcp', 'k8s-web', 'k8s-random-port']
    
    template_path = 'templates/' + challenge_types[chal_type] + '.yml.j2'

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
        result = False

    return result


def destroy_object(k8s_client, template, template_variables):

    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    try:
        k8s_delete_from_yaml.delete_from_yaml(k8s_client, yaml_objects=dep)
    except Exception as e:
        result = False

    return result