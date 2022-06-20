import uuid
import random
from CTFd.utils.config import is_teams_mode
from CTFd.utils.user import get_current_team, get_current_user
from CTFd.utils.decorators import authed_only
from flask import request, Blueprint, render_template

from .k8s_client import get_k8s_client
from .k8s_manage_objects import get_template, deploy_object, destroy_object
from .k8s_database import get_config, insert_challenge_into_tracker, get_challenge_by_id, check_if_port_in_use

def define_k8s_api(app):
    k8s_api = Blueprint('k8s_api', __name__, template_folder='templates', static_folder='assets')

    @k8s_api.route("/k8s_api/create", methods=["POST"])
    @authed_only
    def create():

        options = {}
        config = get_config()

        options['challenge_id'] = request.form['challenge_id']

        if is_teams_mode():
            options['team'] = get_current_team().id
        else:
            options['team'] = ''

        options['user'] = get_current_user().id

        challenge = get_challenge_by_id(options['challenge_id'])

        options['challenge_type'] = challenge.type
        options['instance_id'] = str(uuid.uuid4())
        
        if options['challenge_type'] == 'k8s-random-port':
            test_port = random.randint(45000, 50000)
            while not check_if_port_in_use(test_port):
                test_port = random.randint(45000, 50000)
            options['port'] = test_port
        elif options['challenge_type'] == 'k8s-tcp':
            options['port'] = int(config.external_tcp_port)
        elif options['challenge_type'] == 'k8s-web':
            options['port'] = int(config.external_https_port)

        options['deployment_name'] = 'chal-' + str(challenge.id) + '-' + options['instance_id']
        options['challenge_namespace'] = config.challenge_namespace
        options['container_name'] = challenge.image
        options['challenge_port'] = 8000 #challenge.port
        options['random_port'] = int(options['port'])
        options['istio_namespace'] = config.istio_namespace
        options['istio_ingress_name'] = config.istio_ingress_name
        options['external_tcp_port'] = int(config.external_tcp_port)
        options['external_https_port'] = int(config.external_https_port)
        options['tcp_cert_name'] = config.tcp_domain_name
        options['tcp_domain_name'] = config.tcp_domain_name
        options['https_domain_name'] = config.https_domain_name

        challenge_template = get_template(options['challenge_type'])

        if deploy_object(get_k8s_client(), challenge_template, options):
            insert_challenge_into_tracker(options)
            return "Challenge deployed successfully", 200

        return "Error while creating challenge", 500

    app.register_blueprint(k8s_api)