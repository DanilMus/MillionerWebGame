from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired

class QuestionForm(FlaskForm):
    answer = RadioField('Ответы: ', choices=[], validators=[DataRequired()])
    submit = SubmitField('Ответить')