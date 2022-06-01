from .k8s_challenge import k8sChallengeType, k8sChallenge

from flask import request, Blueprint, jsonify, abort, render_template, url_for, redirect, session

class k8sTcpChallengeType(k8sChallengeType):
    id = "k8s-tcp"
    name = "k8s-tcp"
    templates = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/create.html',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/update.html',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/view.html',
    }
    scripts = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/create.js',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/update.js',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_tcp/view.js',
    }
    route = '/plugins/ctfd-k8s-challenge/assets/k8s_tcp'
    blueprint = Blueprint('ctfd-k8s-challenge', __name__, template_folder='templates', static_folder='assets')

