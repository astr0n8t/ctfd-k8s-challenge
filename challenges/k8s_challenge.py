"""
k8s_challenge

This file implements the challenge class.
"""
from CTFd.models import db, Challenges, Solves, Fails, Flags, Hints, Tags, ChallengeFiles # pylint: disable=import-error
from CTFd.plugins.challenges import BaseChallenge                                         # pylint: disable=import-error
from CTFd.utils.user import get_ip                                                        # pylint: disable=import-error
from CTFd.utils.uploads import delete_file                                                # pylint: disable=import-error

from ..utils import (build_from_repository, delete_challenge_instance,
                     get_challenge_from_tracker, get_challenge_tracker)

class K8sChallengeType(BaseChallenge):
    """
    The base class for all three k8s challenge types.
    """
    id = ""
    name = ""
    templates = {}
    scripts = {}
    route = ''
    blueprint = None

    @staticmethod
    def update(challenge, request):
        """
		This method is used to update the information associated with a challenge.
        This should be kept strictly to the
		Challenges table and any child tables.
		:param challenge:
		:param request:
		:return:
		"""
        data = request.form or request.get_json()

        if (('force-rebuild' in data and data['force-rebuild']) or
             ('repository' in data and data['repository'] != challenge.repository)):
            try:
                data['image'] = build_from_repository(data['name'], data['repository'])
            except Exception as general_exception: # pylint: disable=broad-except
                print("ERROR: ctfd-k8s-challenges: ", general_exception)
                return "Error re-building challenge.  Challenge not updated.", 500
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
        challenge_tracker = get_challenge_tracker()
        for challenge in challenge_tracker:
            delete_challenge_instance(challenge)

        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for uploaded_file in files:
            delete_file(uploaded_file.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        K8sChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def read(challenge):
        """
		This method is in used to access the data of a challenge in a format processable by the front end.
		:param challenge:
		:return: Challenge object, data dictionary to be returned to the user
		"""
        challenge = K8sChallenge.query.filter_by(id=challenge.id).first()
        data = {
            'id': challenge.id,
            'name': challenge.name,
            'value': challenge.value,
            'description': challenge.description,
            'category': challenge.category,
            'state': challenge.state,
            'max_attempts': challenge.max_attempts,
            'type': challenge.type,
            'type_data': {
                'id': K8sChallengeType.id,
                'name': K8sChallengeType.name,
                'templates': K8sChallengeType.templates,
                'scripts': K8sChallengeType.scripts,
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
        try:
            data['image'] = build_from_repository(data['name'], data['repository'])
        except Exception as general_exception: # pylint: disable=broad-except
            print("ERROR: ctfd-k8s-challenges: ", general_exception)
            return "Error building challenge.  Challenge not created.", 500
        challenge = get_k8s_challenge_class(data)
        db.session.add(challenge)
        db.session.commit()
        return challenge

    @staticmethod
    def solve(user, team, challenge, request):
        """
		This method is used to check if the user has solved the challenge.
		:param request:
		:return:
		"""
        delete_challenge_instance(get_challenge_from_tracker(user.id))
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

class K8sChallenge(Challenges):
    """
    Basic model for the database table for the challenge types.
    """
    __mapper_args__ = {'polymorphic_identity': 'k8s-challenge'}
    id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True)
    image = db.Column(db.String(128), index=False)
    repository = db.Column(db.String(128), index=False)
    port = db.Column(db.Integer, index=False)

class K8sTcpChallenge(K8sChallenge):
    """
    Wraps the polymorphic identity for tcp challenges.
    """
    __mapper_args__ = {'polymorphic_identity': 'k8s-tcp'}

class K8sWebChallenge(K8sChallenge):
    """
    Wraps the polymorphic identity for web challenges.
    """
    __mapper_args__ = {'polymorphic_identity': 'k8s-web'}

class K8sRandomPortChallenge(K8sChallenge):
    """
    Wraps the polymorphic identity for random port challenges.
    """
    __mapper_args__ = {'polymorphic_identity': 'k8s-random-port'}


def get_k8s_challenge_class(data):
    """
    Small wrapper function to return the correct class type.
    """
    instance = None
    if data['type'] == 'k8s-tcp':
        instance = K8sTcpChallenge(**data)
    elif data['type'] == 'k8s-web':
        instance = K8sWebChallenge(**data)
    elif data['type'] == 'k8s-random-port':
        instance = K8sRandomPortChallenge(**data)
    return instance
