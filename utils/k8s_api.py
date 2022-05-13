from CTFd.models import db



class k8sChallengeTracker(db.Model):
    """
	K8s Container Tracker. This model stores the users/teams active containers.
	"""
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column("team_id", db.String(64), index=True)
    user_id = db.Column("user_id", db.String(64), index=True)
    image = db.Column("image", db.String(128), index=False)
    timestamp = db.Column("timestamp", db.Integer, index=True)
    revert_time = db.Column("revert_time", db.Integer, index=True)
    instance_id = db.Column("instance_id", db.String(64), index=True)
    port = db.Column("port", db.Integer, index=True)