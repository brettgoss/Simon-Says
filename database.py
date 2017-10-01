# stdlib
import logging
from flask import current_app
from random import randint

# 3rd party
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.attributes import flag_modified

# local

db = SQLAlchemy()

logger = logging.getLogger(__name__)

class Players(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    high_score = db.Column(db.Integer)
    current_score = db.Column(db.Integer)
    moves = db.Column(JSON)


    def __init__(self, un, hs, cs, m):
        self.username = un
        self.high_score = hs
        self.current_score = cs
        self.moves = m


class Database(object):

    def user_exists(self, username):
        user = Players.query.filter_by(username=username).first()
        if user:
            return True
        return False

    def add_move(self, username):
        user = Players.query.filter_by(username=username).first()
        user.moves.append(randint(1, 4))
        moves = user.moves
        flag_modified(user, "moves")
        db.session.commit()
        return moves

    def create_new_user(self, username):
        user = Players(username, None, 0, [])
        db.session.add(user)
        db.session.commit()

    def get_score(self, username):
        user = Players.query.filter_by(username=username).first()
        return user.current_score

    def set_score(self, username, value):
        user = Players.query.filter_by(username=username).first()
        user.current_score = value
        db.session.commit()

    def increment_score(self, username):
        user = Players.query.filter_by(username=username).first()
        user.current_score += 1
        score = user.current_score
        db.session.commit()
        current_app.logger.debug(score)
        return score

    def reset_moves(self, username):
        user = Players.query.filter_by(username=username).first()
        user.moves = []
        flag_modified(user, "moves")
        db.session.commit()
