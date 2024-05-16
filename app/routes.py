from flask import render_template, redirect, url_for

from app import app
from app.forms import QuestionForm
from app.models import Question


@app.route('/question/<int:level>', methods=['GET', 'POST'])
def question(level):
    # Получаем вопрос из базы данных по уровню
    question = Question.query.filter_by(level=level).first()

    # Создаем форму с вариантами ответа из вопроса
    form = QuestionForm()
    form.answer.choices = [(1, question.answer_1), (2, question.answer_2), (3, question.answer_3), (4, question.answer_4)]
    
    if form.validate_on_submit():
        # Проверяем, правильный ли ответ выбрал пользователь
        if int(form.answer.data) == question.num_answer:
            # Пользователь выбрал правильный ответ, увеличиваем его выигрыш
            return redirect(url_for('question', level=level+1))
        else:
            # Пользователь выбрал неправильный ответ, завершаем игру
            pass


    return render_template('question.html', form= form,\
                            question= question.question, level= level)