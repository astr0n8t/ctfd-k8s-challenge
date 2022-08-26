from CTFd.models import db, Challenges, Users
from CTFd.utils.dates import unix_time
from datetime import datetime
from sqlalchemy import text, inspect
from math import floor

from .k8s_config import read_config_file

def init_db():
    existing_config = k8sConfig.query.filter_by(id=1).first()
    if not existing_config: 
        print("ctfd-k8s-challenge: Creating blank config.")
        existing_config = k8sConfig()
    file_config = read_config_file()
    if file_config:
        print("ctfd-k8s-challenge: Reading config from file.")
        columns = [column.name for column in inspect(k8sConfig).c]
        for column in columns:
            if column in file_config and getattr(existing_config, column) != file_config[column]:
                setattr(existing_config, column, file_config[column])
    db.session.add(existing_config)
    db.session.commit()


def get_config():
    return k8sConfig.query.filter_by(id=1).first()

def get_expired_challenges():
    expire_time = int(unix_time(datetime.utcnow()))
    query_str = 'revert_time<' + str(expire_time)
    return k8sChallengeTracker.query.filter(text(query_str)).order_by(text('revert_time')).all()

def extend_challenge_time(challenge):
    extended = False
    config = get_config()
    if challenge.revert_time - unix_time(datetime.utcnow()) < config.expire_interval/2 and (
       challenge.revert_time - unix_time(datetime.utcnow()) > 0):
        challenge.revert_time = challenge.revert_time + floor(config.expire_interval/2)
        db.session.add(challenge)
        db.session.commit()
        extended = True
    return extended

def get_challenge_tracker():
    return k8sChallengeTracker.query.all()

def get_challenge_from_tracker(current_user_id):
    expire_time = int(unix_time(datetime.utcnow()))
    query_str = 'revert_time>' + str(expire_time)
    return k8sChallengeTracker.query.filter_by(user_id=current_user_id).filter(text(query_str)).order_by(text('revert_time')).first()

def get_all_challenges():
    challenges = []

    tracker = get_challenge_tracker()

    for chal in tracker:
        info = {
            'id': chal.challenge_id,
            'instance_id': chal.instance_id,
            'user_id': chal.user_id,
            'user': Users.query.filter_by(id=chal.user_id).first().name,
            'challenge_name': Challenges.query.filter_by(id=chal.challenge_id).first().name
        }
        challenges.append(info)

    return challenges

def insert_challenge_into_tracker(options, expire_time):
    challenge = k8sChallengeTracker()
    challenge.chal_type = options['challenge_type']
    challenge.team_id = options['team']
    challenge.user_id = options['user']
    challenge.challenge_id = options['challenge_id']
    challenge.timestamp = unix_time(datetime.utcnow())
    challenge.revert_time = unix_time(datetime.utcnow()) + expire_time
    challenge.instance_id = options['instance_id']
    challenge.port = options['port']
    db.session.add(challenge)
    db.session.commit()

def remove_challenge_from_tracker(instance_id):
    k8sChallengeTracker.query.filter_by(id=instance_id).delete()
    db.session.commit()
    return

def get_challenge_by_id(challenge_id):
    return Challenges.query.filter_by(id=challenge_id).first()

def check_if_port_in_use(port):
    available = False
    query = k8sChallengeTracker.query.filter_by(port=port).first()

    if not query:
        available = True

    return available

class k8sConfig(db.Model):
    """
	k8s Config Model. This model stores the config for the plugin.
	"""
    id = db.Column(db.Integer, primary_key=True)
    git_credential = db.Column("git_credential", db.String(64), index=False)
    registry_password = db.Column("registry_password", db.String(64), index=False)
    registry_namespace = db.Column("registry_namespace", db.String(64), index=False)
    challenge_namespace = db.Column("challenge_namespace", db.String(64), index=False)
    istio_namespace = db.Column("istio_namespace", db.String(64), index=False)
    tcp_domain_name = db.Column("tcp_domain_name", db.String(64), index=False)
    https_domain_name = db.Column("https_domain_name", db.String(64), index=False)
    certificate_issuer_name = db.Column("certificate_issuer_name", db.String(64), index=False)
    istio_ingress_name = db.Column("istio_ingress_name", db.String(64), index=False)
    external_tcp_port = db.Column("external_tcp_port", db.Integer, index=False)
    external_https_port = db.Column("external_https_port", db.Integer, index=False)
    expire_interval = db.Column("expire_interval", db.Integer, index=False)
    ctfd_url = db.Column("ctfd_url", db.String(64), index=False)

class k8sChallengeTracker(db.Model):
    """
	K8s Container Tracker. This model stores the users/teams active containers.
	"""
    id = db.Column(db.Integer, primary_key=True)
    chal_type = db.Column("type", db.String(64), index=True)
    team_id = db.Column("team_id", db.String(64), index=True)
    user_id = db.Column("user_id", db.String(64), index=True)
    challenge_id = db.Column("challenge_id", db.Integer, index=True)
    timestamp = db.Column("timestamp", db.Integer, index=True)
    revert_time = db.Column("revert_time", db.Integer, index=True)
    instance_id = db.Column("instance_id", db.String(64), index=True)
    port = db.Column("port", db.Integer, index=True)
