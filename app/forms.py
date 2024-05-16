from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    non_burnable_sum = SelectField('Несгораемая сумма', choices=[(500, '500'), (1000, '1000'), (2000, '2000'), (3000, '3000'), (5000, '5000'), (10000, '10000'), (15000, '15000'), (25000, '25000'), (50000, '50000'), (100000, '100000'), (200000, '200000'), (400000, '400000'), (800000, '800000'), (1500000, '1500000'), (3000000, '3000000')], coerce=int)
    submit = SubmitField('Войти')



class QuestionForm(FlaskForm):
    answer = RadioField('Ответы: ', choices=[], validators=[DataRequired()])
    submit = SubmitField('Ответить')