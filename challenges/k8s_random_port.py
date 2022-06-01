from .k8s_challenge import k8sChallengeType, k8sChallenge

from flask import request, Blueprint, jsonify, abort, render_template, url_for, redirect, session

class k8sRandomPortChallengeType(k8sChallengeType):
    id = "k8s-random-port"
    name = "k8s-random-port"
    templates = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/create.html',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/update.html',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/view.html',
    }
    scripts = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/create.js',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/update.js',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_random_port/view.js',
    }
    route = '/plugins/ctfd-k8s-challenge/assets/k8s_random_port'
    blueprint = Blueprint('ctfd-k8s-challenge', __name__, template_folder='templates', static_folder='assets')