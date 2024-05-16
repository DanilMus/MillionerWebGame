from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя: ', validators=[DataRequired()])
    submit = SubmitField('Начать игру')


class QuestionForm(FlaskForm):
    answer = RadioField('Ответы: ', choices=[], validators=[DataRequired()])
    submit = SubmitField('Ответить')