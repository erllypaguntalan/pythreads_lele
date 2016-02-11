from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from .models import User

class ThreadForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[Length(min=0, max=140)])
    choices = ['News', 'Music', 'Movies', 'Gaming', 'Anime', 'Others']
    topic = SelectField('topics', choices=[(c, c) for c in choices], validators=[DataRequired()])

class EditForm(Form):
	title = StringField('title', validators=[DataRequired()])
	body = TextAreaField('body', validators=[Length(min=0, max=140), DataRequired()])

class CommentForm(Form):
	body = TextAreaField('body', validators=[Length(min=0, max=140), DataRequired()])