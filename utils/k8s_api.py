import uuid
import base64
import random
import urllib.parse
from datetime import datetime
from CTFd.utils.config import is_teams_mode
from CTFd.utils.user import get_current_team, get_current_user, is_admin
from CTFd.utils.decorators import admins_only, authed_only, ratelimit
from flask import request, Blueprint, render_template, redirect

from .k8s_client import get_k8s_client, get_k8s_v1_client
from .k8s_manage_objects import get_template, deploy_object, destroy_object, add_ingress_port, delete_ingress_port
from .k8s_database import *

def define_k8s_api(app):
    k8s_api = Blueprint('k8s_api', __name__, template_folder='templates', static_folder='assets')

    @k8s_api.route("/api/v1/k8s/create", methods=["POST"])
    @authed_only
    @ratelimit(method="POST", limit=20, interval=300, key_prefix="rl")
    def create():
        try:
            user_current_challenge = get_challenge_from_tracker(get_current_user().id)

            if user_current_challenge:
                return "User already has a challenge instance running", 200

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
                test_port = random.randint(40000, 50000)
                while not check_if_port_in_use(test_port):
                    test_port = random.randint(40000, 50000)
                if add_ingress_port(get_k8s_v1_client(), config, test_port):
                    options['port'] = test_port
                else:
                    return "Error while creating challenge", 500
            elif options['challenge_type'] == 'k8s-tcp':
                options['port'] = int(config.external_tcp_port)
            elif options['challenge_type'] == 'k8s-web':
                options['port'] = int(config.external_https_port)

            options['deployment_name'] = 'chal-' + options['instance_id']
            options['challenge_namespace'] = config.challenge_namespace
            options['container_name'] = challenge.image
            options['challenge_port'] = challenge.port
            options['random_port'] = int(options['port'])
            options['istio_namespace'] = config.istio_namespace
            options['istio_ingress_name'] = config.istio_ingress_name
            options['external_tcp_port'] = int(config.external_tcp_port)
            options['external_https_port'] = int(config.external_https_port)
            options['tcp_cert_name'] = config.tcp_domain_name
            options['tcp_domain_name'] = config.tcp_domain_name
            options['https_domain_name'] = config.https_domain_name

            registry_auth = base64.b64encode(str('ctfd:'+config.registry_password).encode('ascii')).decode('ascii')
            options['registry_data'] = base64.b64encode(str('{"auths":{"chal-registry.' + config.https_domain_name + '":{"username":"ctfd","password":"' + config.registry_password + '","auth":"' + registry_auth + '"}' + '}' + '}').encode('ascii')).decode('ascii')

            challenge_template = get_template(options['challenge_type'])

            if deploy_object(get_k8s_client(), challenge_template, options):
                insert_challenge_into_tracker(options, config.expire_interval)

                redirect_url = request.referrer + '#' + urllib.parse.quote_plus(challenge.name) + '-' + str(challenge.id)
                return redirect(redirect_url), 302
        except Exception as e:
            print("ERROR: ctfd-k8s-challenges: ", e)

        return "Error while creating challenge", 500

    @k8s_api.route("/api/v1/k8s/get", methods=["GET"])
    @authed_only
    @ratelimit(method="GET", limit=300, interval=300, key_prefix="rl")
    def get():
        try:
            information = {'InstanceRunning': False, 'ThisChallengeInstance': False, 'ExpireTime': 0}

            challenge = get_challenge_from_tracker(get_current_user().id)

            if challenge:
                challenge_id = int(request.args.get('challenge_id'))
                if challenge.challenge_id == challenge_id:
                    config = get_config()

                    if challenge.chal_type == 'k8s-web':
                        information['ConnectionURL'] = str('https://chal-' + challenge.instance_id + '.' + config.https_domain_name)
                    else:
                        information['ConnectionURL'] = str('chal-' + challenge.instance_id + '.' + config.tcp_domain_name)
                    information['ConnectionPort'] = challenge.port
                    information['InstanceRunning'] = True
                    information['ThisChallengeInstance'] = True
                    information['ExpireTime'] = int(challenge.revert_time)
                    if information['ExpireTime'] - unix_time(datetime.utcnow()) < config.expire_interval/2 and (
                    information['ExpireTime'] - unix_time(datetime.utcnow()) > 0):
                        information['ExtendAvailable'] = True
                    else:
                        information['ExtendAvailable'] = False
                else:
                    information['InstanceRunning'] = True
            return information, 200
        except Exception as e:
            print("ERROR: ctfd-k8s-challenges: ", e)

        return "Error retrieving info", 500

    @k8s_api.route("/api/v1/k8s/delete", methods=["POST"])
    @authed_only
    @ratelimit(method="POST", limit=20, interval=300, key_prefix="rl")
    def delete():
        try:
            if is_admin() and 'user_id' in request.form:
                user_id = request.form['user_id']
            else:
                user_id = get_current_user().id

            challenge = get_challenge_from_tracker(user_id)

            if challenge and challenge.challenge_id == int(request.form['challenge_id']):
                if delete_challenge_instance(challenge):
                    return redirect(request.referrer), 302
            else:
                return redirect(request.referrer), 302

        except Exception as e:
            print("ERROR: ctfd-k8s-challenges: ", e)

        return "Error while deleting challenges", 500

    @k8s_api.route("/api/v1/k8s/delete_all", methods=["POST"])
    @admins_only
    def delete_all():
        try:
            challenge_tracker = get_challenge_tracker()
            success = True

            for challenge in challenge_tracker:
                if not delete_challenge_instance(challenge):
                    success = False
                
            if success:
                return redirect(request.referrer), 302

        except Exception as e:
            print("ERROR: ctfd-k8s-challenges: ", e)

        return "Error while deleting challenges", 500

    @k8s_api.route("/api/v1/k8s/clean", methods=["GET"])
    @ratelimit(method="GET", limit=20, interval=300, key_prefix="rl")
    def clean():
        try:
            challenges = get_expired_challenges()
            for challenge in challenges:
                delete_challenge_instance(challenge)
            return "", 200
        except Exception as e:
            print("ERROR: ctfd-k8s-challenges: ", e)
        
        return "An error occurred while cleaning.", 500

    @k8s_api.route("/api/v1/k8s/extend", methods=["POST"])
    @ratelimit(method="POST", limit=20, interval=300, key_prefix="rl")
    def extend():
        try:
            challenge = get_challenge_from_tracker(get_current_user().id)

            if challenge:
                if challenge.challenge_id == int(request.form['challenge_id']):
                    if extend_challenge_time(challenge):
                        chal = get_challenge_by_id(int(request.form['challenge_id']))
                        redirect_url = request.referrer + '#' + urllib.parse.quote_plus(chal.name) + '-' + str(chal.id)
                        return redirect(redirect_url), 302 
            
            return redirect(request.referrer), 302

        except Exception as e:
            print("ERROR: ctfd-k8s-challenges: ", e)
        
        return "An error occurred while extending.", 500

    app.register_blueprint(k8s_api)

def delete_challenge_instance(challenge):
    deleted = False
    options = {}
    config = get_config()

    options['deployment_name'] = 'chal-' + str(challenge.instance_id)
    options['challenge_namespace'] = config.challenge_namespace
    options['istio_namespace'] = config.istio_namespace
    challenge_template = get_template(challenge.chal_type)
    if destroy_object(get_k8s_client(), challenge_template, options):
        if challenge.chal_type == 'k8s-random-port':
            delete_ingress_port(get_k8s_v1_client(), config, challenge.port)
        remove_challenge_from_tracker(challenge.id)
        deleted = True

    return deleted