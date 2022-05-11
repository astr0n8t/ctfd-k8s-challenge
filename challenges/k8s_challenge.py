from CTFd.models import db, Challenges
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class
from flask import request, Blueprint, jsonify, abort, render_template, url_for, redirect, session

class k8sChallengeType(BaseChallenge):
    id = "k8s-challenge"
    name = "k8s-challenge"
    templates = {
        'create': '/plugins/ctfd-k8s-challenge/assets/create.html',
        'update': '/plugins/ctfd-k8s-challenge/assets/update.html',
        'view': '/plugins/ctfd-k8s-challenge/assets/view.html',
    }
    scripts = {
        'create': '/plugins/ctfd-k8s-challenge/assets/create.js',
        'update': '/plugins/ctfd-k8s-challenge/assets/update.js',
        'view': '/plugins/ctfd-k8s-challenge/assets/view.js',
    }
    route = '/plugins/ctfd-k8s-challenge/assets'
    blueprint = Blueprint('ctfd-k8s-challenge', __name__, template_folder='templates', static_folder='assets')

    @staticmethod
    def update(challenge, request):
        """
		This method is used to update the information associated with a challenge. This should be kept strictly to the
		Challenges table and any child tables.
		:param challenge:
		:param request:
		:return:
		"""
        data = request.form or request.get_json()
        for attr, value in data.items():
            setattr(challenge, attr, value)

        db.session.commit()
        return challenge

    @staticmethod
    def delete(challenge):
        """
		This method is used to delete the resources used by a challenge.
		NOTE: Will need to kill all containers here
		:param challenge:
		:return:
		"""
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        k8sChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def read(challenge):
        """
		This method is in used to access the data of a challenge in a format processable by the front end.
		:param challenge:
		:return: Challenge object, data dictionary to be returned to the user
		"""
        challenge = k8sChallenge.query.filter_by(id=challenge.id).first()
        data = {
            'id': challenge.id,
            'name': challenge.name,
            'value': challenge.value,
            'image': challenge.image,
            'description': challenge.description,
            'category': challenge.category,
            'state': challenge.state,
            'max_attempts': challenge.max_attempts,
            'type': challenge.type,
            'type_data': {
                'id': k8sChallengeType.id,
                'name': k8sChallengeType.name,
                'templates': k8sChallengeType.templates,
                'scripts': k8sChallengeType.scripts,
            }
        }
        return data

    @staticmethod
    def create(request):
        """
		This method is used to process the challenge creation request.
		:param request:
		:return:
		"""
        data = request.form or request.get_json()
        challenge = k8sChallenge(**data)
        db.session.add(challenge)
        db.session.commit()
        return challenge

    @staticmethod
    def attempt(challenge, request):
        """
		This method is used to check whether a given input is right or wrong. It does not make any changes and should
		return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
		user's input from the request itself.
		:param challenge: The Challenge object from the database
		:param request: The request the user submitted
		:return: (boolean, string)
		"""

        data = request.form or request.get_json()
        print(request.get_json())
        print(data)
        submission = data["submission"].strip()
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            if get_flag_class(flag.type).compare(flag, submission):
                return True, "Correct"
        return False, "Incorrect"

    @staticmethod
    def solve(user, team, challenge, request):
        """
		This method is used to insert Solves into the database in order to mark a challenge as solved.
		:param team: The Team object from the database
		:param chal: The Challenge object from the database
		:param request: The request the user submitted
		:return:
		"""
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission,
        )
        db.session.add(solve)
        db.session.commit()

    @staticmethod
    def fail(user, team, challenge, request):
        """
		This method is used to insert Fails into the database in order to mark an answer incorrect.
		:param team: The Team object from the database
		:param chal: The Challenge object from the database
		:param request: The request the user submitted
		:return:
		"""
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        wrong = Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=submission,
        )
        db.session.add(wrong)
        db.session.commit()

class k8sChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'k8s-challenge'}
    id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
    image = db.Column(db.String(128), index=True)  

class k8sChallengeTracker(db.Model):
    """
	K8s Container Tracker. This model stores the users/teams active containers.
	"""
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column("team_id", db.String(64), index=True)
    user_id = db.Column("user_id", db.String(64), index=True)
    image = db.Column("image", db.String(128), index=True)
    timestamp = db.Column("timestamp", db.Integer, index=True)
    revert_time = db.Column("revert_time", db.Integer, index=True)
    instance_id = db.Column("instance_id", db.String(128), index=True)
    port = db.Column("port", db.Integer, index=True)