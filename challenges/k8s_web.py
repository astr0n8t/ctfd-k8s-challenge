from .k8s_challenge import k8sChallengeType, k8sChallenge

from flask import request, Blueprint, jsonify, abort, render_template, url_for, redirect, session

class k8sWebChallengeType(k8sChallengeType):
    id = "k8s-web"
    name = "k8s-web"
    templates = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_web/create.html',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_web/update.html',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_web/view.html',
    }
    scripts = {
        'create': '/plugins/ctfd-k8s-challenge/assets/k8s_web/create.js',
        'update': '/plugins/ctfd-k8s-challenge/assets/k8s_web/update.js',
        'view': '/plugins/ctfd-k8s-challenge/assets/k8s_web/view.js',
    }
    route = '/plugins/ctfd-k8s-challenge/assets/k8s_web'
    blueprint = Blueprint('ctfd-k8s-challenge', __name__, template_folder='templates', static_folder='assets')

