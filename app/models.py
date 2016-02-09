from app import db
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    nickname = db.Column(db.String(64), nullable=False)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True)
    about_me = db.Column(db.String(200), nullable=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)