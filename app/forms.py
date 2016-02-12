from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from .models import User

class ThreadForm(Form):
    title = StringField('title')
    body = TextAreaField('body')
    choices = ['News', 'Music', 'Movies', 'Gaming', 'Anime', 'Others']
    topic = SelectField('topics', choices=[(c, c) for c in choices])

class EditForm(Form):
	title = StringField('title')
	body = TextAreaField('body')

class CommentForm(Form):
	body = TextAreaField('body')