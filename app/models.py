from app import db
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin

tracks = db.Table('tracks',
    db.Column('thread_id', db.Integer, db.ForeignKey('thread.id')),
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'))
)


class Thread(db.Model):
	__tablename__ = 'thread'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	body = db.Column(db.String(200))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	topic = db.Column(db.String(50))

	def __repr__(self):
		return '<Thread %r>' % (self.title)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    nickname = db.Column(db.String(64), nullable=False)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True)
    about_me = db.Column(db.String(200), nullable=True)
    threads = db.relationship('Thread', backref='author', lazy='dynamic')
    tracked = db.relationship('Thread',
    							secondary=tracks,
    							primaryjoin=(tracks.c.follower_id == id),
    							secondaryjoin=(tracks.c.thread_id == Thread.id),
    							backref=db.backref('tracks', lazy='dynamic'),
    							lazy='dynamic')

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

    def track(self, thread):
        if not self.is_tracked(thread):
            self.tracked.append(thread)
            return self
        else:
            return self

    def untrack(self, thread):
        if self.is_tracked(thread):
            self.tracked.remove(thread)
            return self

    def is_tracked(self, thread):
        return self.tracked.filter(tracks.c.thread_id == thread.id).count() > 0

    def __repr__(self):
        return '<User %r>' % (self.nickname)