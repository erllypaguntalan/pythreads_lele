from app import app, db, lm
from datetime import datetime
from flask import g, flash, render_template, redirect, request, session, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import ThreadForm, EditForm, CommentForm
from .models import User, Thread, Comment
from .oauth import OAuthSignIn

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ThreadForm()
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
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, body=form.body.data, topic=form.topic.data, date_created=datetime.utcnow(), author=g.user)
        db.session.add(thread)
        db.session.commit()
        flash('Your thread is now live!')
        return redirect(url_for('index'))
    return render_template('index.html', topics=topics, form=form)


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
@app.route('/user/<nickname>', methods=['GET', 'POST'])
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    threads = user.threads
    tracks = Thread.query.all()
    return render_template('user.html',
                           user=user,
                           threads=threads,
                           tracks=tracks)


@app.route('/topic/<topicname>')
@app.route('/topic/<topicname>', methods=['GET', 'POST'])
@login_required
def topic(topicname):
    if topicname == None:
        flash('Topic %s not found.' % topicname)
        return redirect(url_for('index'))

    threads = Thread.query.filter_by(topic=topicname).order_by(Thread.date_created.desc())
    return render_template('topic.html',
                            topic=topicname, threads=threads)


@app.route('/edit_thread/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_thread(id):
    form = EditForm()
    thread = Thread.query.get(id)
    if thread is None:
        flash('Thread not found.')
        return redirect(url_for('index'))
    if thread.author.id != g.user.id:
        flash('You cannot edit this thread.')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        thread.title = form.title.data
        thread.body = form.body.data
        db.session.add(thread)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('thread', id=id))
    elif request.method != "POST":
        form.title.data = thread.title
        form.body.data = thread.body
    return render_template('edit_thread.html', form=form, thread=thread)

@app.route('/delete_thread/<int:id>')
@login_required
def delete_thread(id):
    thread = Thread.query.get(id)
    if thread is None:
        flash('Thread not found.')
        return redirect(url_for('index'))
    if thread.author.id != g.user.id:
        flash('You cannot delete this thread.')
        return redirect(url_for('thread', id=id))
    db.session.delete(thread)
    db.session.commit()
    flash('Your thread has been deleted.')
    return redirect(url_for('index'))


@app.route('/track/<int:id>')
@login_required
def track(id):
    thread = Thread.query.get(id)
    if thread is None:
        flash('Thread not found.')
        return redirect(url_for('index'))
    track = g.user.track(thread)
    if track is None:
        flash('Cannot track thread')
        return redirect(url_for('thread', id=id))
    db.session.add(track)
    db.session.commit()
    flash('Thread is now tracked!')
    return redirect(url_for('thread', id=id))

@app.route('/untrack/<int:id>')
@login_required
def untrack(id):
    thread = Thread.query.get(id)
    if thread is None:
        flash('Thread not found.')
        return redirect(url_for('index'))
    untrack = g.user.untrack(thread)
    if untrack is None:
        flash('Cannot untrack thread.')
        return redirect(url_for('thread', id=id))
    db.session.add(untrack)
    db.session.commit()
    flash('Thread untracked.')
    return redirect(url_for('thread', id=id))


@app.route('/thread/<int:id>', methods=['GET', 'POST'])
@login_required
def thread(id):
    thread = Thread.query.filter_by(id=id).first()
    form = CommentForm()
    if thread is None:
        flash('Thread not found.')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, date_created=datetime.utcnow(), c_author=g.user, c_thread=thread)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('thread', id=thread.id))
    comments = thread.comments
    return render_template('thread.html', thread=thread, form=form, comments=comments)


@app.route('/edit_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    form = CommentForm()
    comment = Comment.query.get(id)
    if comment is None:
        flash('Comment not found.')
        return redirect(url_for('index'))
    if comment.c_author.id != g.user.id:
        flash('You cannot edit this comment.')
        return redirect(url_for('thread', id=comment.thread_id))
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('thread', id=comment.thread_id))
    elif request.method != "POST":
        form.body.data = comment.body
    return render_template('edit_comment.html', form=form)

@app.route('/delete_comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comment.query.get(id)
    if comment is None:
        flash('Comment not found.')
        return redirect(url_for('index'))
    if comment.c_author.id != g.user.id:
        flash('You cannot delete this comment.')
        return redirect(url_for('thread', id=comment.thread_id))
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.')
    return redirect(url_for('thread', id=comment.thread_id))


@app.route('/like/<int:id>')
@login_required
def like(id):
    comment = Comment.query.get(id)
    if comment is None:
        flash('Comment not found.')
        return redirect(url_for('index'))
    like = g.user.like(comment)
    if like is None:
        flash('Cannot like comment')
        return redirect(url_for('thread', id=comment.thread_id))
    db.session.add(like)
    db.session.commit()
    flash('Comment is now liked!')
    return redirect(url_for('thread', id=comment.thread_id))

@app.route('/unlike/<int:id>')
@login_required
def unlike(id):
    comment = Comment.query.get(id)
    if comment is None:
        flash('Comment not found.')
        return redirect(url_for('index'))
    unlike = g.user.unlike(comment)
    if unlike is None:
        flash('Cannot unlike comment.')
        return redirect(url_for('thread', id=comment.thread_id))
    db.session.add(unlike)
    db.session.commit()
    flash('Comment unlike.')
    return redirect(url_for('thread', id=comment.thread_id))