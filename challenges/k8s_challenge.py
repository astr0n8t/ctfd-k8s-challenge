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

class k8sChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'k8s-challenge'}
    id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True)
    image = db.Column(db.String(128), index=False)  
    repository = db.Column(db.String(128), index=False)  

