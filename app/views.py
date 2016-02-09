from app import app, db, lm
from config import POSTS_PER_PAGE
from datetime import datetime
from flask import g, flash, render_template, redirect, request, session, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import ThreadForm
from .models import User, Thread
from .oauth import OAuthSignIn

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    topics = {'News', 'Music', 'Movies', 'Gaming', 'Anime', 'Others'}
    form = ThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, body=form.body.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(thread)
        db.session.commit()
        flash('Your thread is now live!')
        return redirect(url_for('index'))
    threads = g.user.threads.paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', form=form, topics=topics, threads=threads)


#------------FACEBOOK LOGIN----------------------------------------------
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=email.split('@')[0], email=email, name=username)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))
#------------------------------------------------------------------------  


@app.route('/login')
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)

@app.route('/topic/<topicname>')
def topic(topicname):
    if topicname == None:
        flash('Topic %s not found.' % topicname)
        return redirect(url_for('index'))

    return render_template('topic.html',
                            topic=topicname)