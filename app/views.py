from app import app, db, lm
from config import POSTS_PER_PAGE
from datetime import datetime
from flask import g, flash, render_template, redirect, request, session, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import ThreadForm, EditForm
from .models import User, Thread
from .oauth import OAuthSignIn
from sqlalchemy import func

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    topics = {
        'News': {'count': 0},
        'Music': {'count': 0},
        'Movies': {'count': 0},
        'Gaming': {'count': 0},
        'Anime': {'count': 0},
        'Others': {'count': 0}
    }
    for topic in topics:
        count = Thread.query.filter_by(topic=topic).count()
        topics[topic]['count'] = count  
    return render_template('index.html', topics=topics)


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
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    threads = user.threads.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           threads=threads)

@app.route('/topic/<topicname>')
@app.route('/topic/<topicname>/<int:page>', methods=['GET', 'POST'])
def topic(topicname, page=1):
    if topicname == None:
        flash('Topic %s not found.' % topicname)
        return redirect(url_for('index'))

    threads = Thread.query.filter_by(topic=topicname).paginate(page, POSTS_PER_PAGE, False)
    return render_template('topic.html',
                            topic=topicname, threads=threads)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, body=form.body.data, topic=form.topic.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(thread)
        db.session.commit()
        flash('Your thread is now live!')
        return redirect(url_for('index'))
    return render_template('create.html', form=form)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = EditForm()
    thread = Thread.query.get(id)

    if thread is None:
        flash('Thread not found.')
        return redirect(url_for('index'))

    if thread.author.id != g.user.id:
        flash('You cannot delete this thread.')
        return redirect(url_for('index'))
    
    if form.validate_on_submit():
        thread.title = form.title.data
        thread.body = form.body.data
        db.session.add(thread)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', nickname=g.user.nickname))

    elif request.method != "POST":
        form.title.data = thread.title
        form.body.data = thread.body

    return render_template('edit_thread.html', form=form)