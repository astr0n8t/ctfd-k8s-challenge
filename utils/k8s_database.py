from CTFd.models import db

def init_db():
    existing_config = k8sConfig.query.filter_by(id=1).first()
    if not existing_config: 
        print("ctfd-k8s-challenge: Creating new config with defaults.")
        config = k8sConfig()
        config.git_credential = ""
        config.registry_namespace = "registry"
        config.challenge_namespace = "challenges"
        config.istio_namespace = "istio-system"
        config.tcp_domain_name = "chal.luctf.dev"
        config.https_domain_name = "web.luctf.dev"
        config.certificate_issuer_name = "cloudflare-istio-issuer"
        config.istio_ingress_name = "istio-ingressgateway"
        config.external_tcp_port = 443
        config.external_https_port = 443
        db.session.add(config)
        db.session.commit()
    else:
        print("ctfd-k8s-challenge: Using existing config.")

def get_config():
    return k8sConfig.query.filter_by(id=1).first()


class k8sConfig(db.Model):
    """
	k8s Config Model. This model stores the config for the plugin.
	"""
    id = db.Column(db.Integer, primary_key=True)
    git_credential = db.Column("git_credential", db.String(64), index=False)
    registry_namespace = db.Column("registry_namespace", db.String(64), index=False)
    challenge_namespace = db.Column("challenge_namespace", db.String(64), index=False)
    istio_namespace = db.Column("istio_namespace", db.String(64), index=False)
    tcp_domain_name = db.Column("tcp_domain_name", db.String(64), index=False)
    https_domain_name = db.Column("https_domain_name", db.String(64), index=False)
    certificate_issuer_name = db.Column("certificate_issuer_name", db.String(64), index=False)
    istio_ingress_name = db.Column("istio_ingress_name", db.String(64), index=False)
    external_tcp_port = db.Column("external_tcp_port", db.Integer, index=False)
    external_https_port = db.Column("external_https_port", db.Integer, index=False)

