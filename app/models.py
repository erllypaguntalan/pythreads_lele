from app import db
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin

tracks = db.Table('tracks',
    db.Column('thread_id', db.Integer, db.ForeignKey('thread.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

likes = db.Table('likes',
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class Thread(db.Model):
    __tablename__ = 'thread'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(5000))
    date_created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topic = db.Column(db.String(50))
    comments = db.relationship('Comment', backref='c_thread', lazy='dynamic')

    def __repr__(self):
        return '<Thread %r>' % (self.title)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

    def __repr__(self):
        return '<Comment %r>' % (self.date_created)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    nickname = db.Column(db.String(64), nullable=False)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True)
    threads = db.relationship('Thread', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='c_author', lazy='dynamic')
    tracked = db.relationship('Thread',
                                secondary=tracks,
                                primaryjoin=(tracks.c.followed_id == id),
                                secondaryjoin=(tracks.c.thread_id == Thread.id),
                                backref=db.backref('tracks', lazy='dynamic'),
                                lazy='dynamic')
    liked = db.relationship('Comment',
                                secondary=likes,
                                primaryjoin=(likes.c.followed_id == id),
                                secondaryjoin=(likes.c.comment_id == Comment.id),
                                backref=db.backref('likes', lazy='dynamic'),
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

    def track(self, post):
        if not self.is_tracked(post):
            self.tracked.append(post)
            return self
        else:
            return self

    def untrack(self, post):
        if self.is_tracked(post):
            self.tracked.remove(post)
            return self

    def is_tracked(self, post):
        return self.tracked.filter(tracks.c.thread_id == post.id).count() > 0

    def like(self, post):
        if not self.is_liked(post):
            self.liked.append(post)
            return self
        else:
            return self

    def unlike(self, post):
        if self.is_liked(post):
            self.liked.remove(post)
            return self

    def is_liked(self, post):
        return self.liked.filter(likes.c.comment_id == post.id).count() > 0

    def __repr__(self):
        return '<User %r>' % (self.nickname)


def Save(model):
    db.session.add(model)
    db.session.commit()
    
def Delete(model):
    db.session.delete(model)
    db.session.commit()