from CTFd.utils.decorators import admins_only
from CTFd.forms.fields import SubmitField
from CTFd.forms import BaseForm
from CTFd.models import db
from flask import request, Blueprint, render_template
from wtforms import (
    FileField,
    HiddenField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    SelectMultipleField,
    BooleanField,
)
from ..utils import get_config, get_all_challenges

class k8sConfigForm(BaseForm):
    id = HiddenField()
    git_credential = PasswordField(
        "Git Repository Credential", description="The secret used to access private Git repositories."
    )
    registry_namespace = StringField(
        "Registry Namespace", description="The namespace to deploy the internal container registry to."
    )
    challenge_namespace = StringField(
        "Challenge Namespace", description="The namespace to deploy challenges to."
    )
    istio_namespace = StringField(
        "Istio Namespace", description="The namespace where istio is deployed to."
    )
    tcp_domain_name = StringField(
        "TCP Domain Name", description="The domain name for TCP challenges."
    )
    https_domain_name = StringField(
        "Web Domain Name", description="The domain name for web challenges."
    )
    certificate_issuer_name = StringField(
        "Certificate Issuer Name", description="The name of the certificate issuer in the cluster."
    )
    istio_ingress_name = StringField(
        "Istio Ingress Name", description="The name of the cluster Istio Ingress Gateway."
    )
    external_tcp_port = StringField(
        "External TCP Port", description="The port that TCP/TLS challenges are exposed on."
    )
    external_https_port = StringField(
        "External Web Port", description="The port that web challenges are exposed on."
    )
    expire_interval = StringField(
        "Expire Interval", description="The time before a challenge instance expires in seconds."
    )
    ctfd_url = StringField(
        "CTFd URL", description="The URL that CTFd is accessible from within the cluster."
    )
    submit = SubmitField('Submit')

def define_k8s_admin(app):
    k8s_admin = Blueprint('k8s_admin', __name__, template_folder='templates', static_folder='assets')

    @k8s_admin.route("/admin/kubernetes", methods=["GET", "POST"])
    @admins_only
    def admin():
        config = get_config()
        form = k8sConfigForm()
        challenge_instances = []

        if request.method == "GET":
            challenge_instances = get_all_challenges()

        elif request.method == "POST":

            if len(request.form['git_credential']) > 0:
                config.git_credential = request.form['git_credential']
            if config.registry_namespace != request.form['registry_namespace']:
                config.registry_namespace = request.form['registry_namespace']
            if config.challenge_namespace != request.form['challenge_namespace']:
                config.challenge_namespace = request.form['challenge_namespace']
            if config.istio_namespace != request.form['istio_namespace']:
                config.istio_namespace = request.form['istio_namespace']
            if config.tcp_domain_name != request.form['tcp_domain_name']:
                config.tcp_domain_name = request.form['tcp_domain_name']
            if config.https_domain_name != request.form['https_domain_name']:
                config.https_domain_name = request.form['https_domain_name']
            if config.certificate_issuer_name != request.form['certificate_issuer_name']:
                config.certificate_issuer_name = request.form['certificate_issuer_name']
            if config.istio_ingress_name != request.form['istio_ingress_name']:
                config.istio_ingress_name = request.form['istio_ingress_name']
            if config.external_tcp_port != int(request.form['external_tcp_port']):
                config.external_tcp_port = int(request.form['external_tcp_port'])
            if config.external_https_port != int(request.form['external_https_port']):
                config.external_https_port = int(request.form['external_https_port'])
            if config.expire_interval != int(request.form['expire_interval']):
                config.expire_interval = int(request.form['expire_interval'])
            if config.ctfd_url != request.form['ctfd_url']:
                config.ctfd_url = request.form['ctfd_url']

            db.session.commit()

        return render_template("plugins/ctfd-k8s-challenge/assets/k8s_admin.html", config=config, form=form, challenge_instances=challenge_instances)

    app.register_blueprint(k8s_admin)