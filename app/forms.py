from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя: ', validators=[DataRequired()])
    non_burnable_sum = SelectField('Несгораемая сумма: ', choices=[(500, '500'), (1000, '1000'), (2000, '2000'), (3000, '3000'), (5000, '5000'), (10000, '10000'), (15000, '15000'), (25000, '25000'), (50000, '50000'), (100000, '100000'), (200000, '200000'), (400000, '400000'), (800000, '800000'), (1500000, '1500000')], coerce=int)
    hints = SelectMultipleField('Подсказки: ', choices=[('hint1', 'Помощь из зала'), ('hint2', '50 на 50'), ('hint3', 'Звонок другу'), ('hint4', 'Право на ошибку'), ('hint5', 'Замена вопроса')], validators=[Length(min=3, max=3, message="Вы должны выбрать ровно 3 подсказки.")])
    submit = SubmitField('Войти')



class QuestionForm(FlaskForm):
    answer = RadioField('Ответы: ', choices=[], validators=[DataRequired()])
    submit = SubmitField('Ответить')
    hint1 = SubmitField('Помощь из зала')
    hint2 = SubmitField('50 на 50')
    hint3 = SubmitField('Звонок другу')
    hint4 = SubmitField('Право на ошибку')
    hint5 = SubmitField('Замена вопроса')