from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
#from wtforms.widgets import TextArea
from .models import User

class ThreadForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[Length(min=0, max=140)])