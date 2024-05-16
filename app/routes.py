from flask import render_template, redirect, url_for
from flask import session

from app import app, db
from app.forms import QuestionForm, LoginForm
from app.models import Question, User

rating = [500, 1000, 2000, 3000, 5000, 10000, 15000, 25000, 50000, 100000, 200000, 400000, 800000, 1500000, 3000000]


# Начало игры
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            # Пользователя нет в базе данных, создаем нового
            user = User(username=form.username.data, record=0, non_burnable_sum=form.non_burnable_sum.data)
            db.session.add(user)
        else:
            # Пользователь уже существует, обновляем его несгораемую сумму
            user.non_burnable_sum = form.non_burnable_sum.data
        db.session.commit()

        # Сохраняем id пользователя в сессии
        session['user_id'] = user.id

        # Перенаправляем пользователя на страницу вопросов
        return redirect(url_for('question', level=1))
    
    return render_template('login.html', form=form)


# Сама игра
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
            if level == 15:
                # Пользователь дошел до последнего уровня, перенаправляем на страницу завершения игры
                return redirect(url_for('end', level=level))
            else:
                return redirect(url_for('question', level=level+1))
        else:
            # Пользователь выбрал неправильный ответ, перенаправляем на страницу завершения игры
            return redirect(url_for('end', level=level))

    return render_template('question.html', form=form,
                            question=question.question, level=level,
                            rating= rating)


# Завершение игры с результатами
@app.route('/end/<int:level>', methods=['GET'])
def end(level):
    # Получаем пользователя из базы данных по id
    user = User.query.get(session['user_id'])

    # Проверяем, достиг ли пользователь несгораемой суммы
    if level < len(rating) and rating[level-1] > user.non_burnable_sum:
        user.record = max(user.record, user.non_burnable_sum)
        message = f"Вы дошли до уровня {level} и заработали {user.record}."
    # Проверяем, дошел ли пользователь до последнего уровня
    elif level == len(rating):
        user.record = max(user.record, rating[level-1])
        message = "Поздравляем! Вы дошли до последнего уровня и стали миллионером!"
    # Проверяем проиграл ли игрок
    else:
        message = f"Вы дошли до уровня {level}, но ничего не получили. Не отчаивайтесь, попробуйте еще раз!"
    
    db.session.commit()

    # Получаем список пользователей, отсортированный по рекордам
    users = User.query.order_by(User.record.desc()).limit(10).all()

    return render_template('end.html', message=message, users= users)
