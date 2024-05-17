from flask import render_template, redirect, url_for
from flask import session, request

from sqlalchemy.sql.expression import func

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
            user = User(username= form.username.data, record= 0, 
                        non_burnable_sum= form.non_burnable_sum.data, hints=form.hints.data)
            db.session.add(user)
        else:
            # Пользователь уже существует, обновляем его несгораемую сумму
            user.non_burnable_sum = form.non_burnable_sum.data
            user.hints = form.hints.data
        db.session.commit()

        # Сохраняем id пользователя в сессии
        session['user_id'] = user.id

        # Перенаправляем пользователя на страницу вопросов
        return redirect(url_for('question', level=1))
    
    return render_template('login.html', form=form)




# Сама игра
@app.route('/question/<int:level>', methods=['GET', 'POST'])
def question(level):
    # Получаем пользователя из базы данных по id
    user = User.query.get(session['user_id'])
    
    if 'question_id' not in session:
        # Получаем вопрос из базы данных по уровню
        question = Question.query.filter_by(level=level).order_by(func.random()).first()
        session['question_id'] = question.id
    else:
        question = Question.query.get(session['question_id'])


    # Создаем форму с вариантами ответа из вопроса
    form = QuestionForm()
    form.answer.choices = [
        (1, question.answer_1), 
        (2, question.answer_2), 
        (3, question.answer_3), 
        (4, question.answer_4)
    ]
    
    # Проход по подсказкам и проверка на то, есть ли возможность ими воспользоваться
    if form.hint1.data or form.hint2.data or form.hint3.data \
        or form.hint4.data or form.hint5.data:

        new_hints = user.hints.copy()  # Создаем копию списка подсказок (нужно из-за особенностей удаления в sqlalchemy)

        # hint1 - Помощь из зала
        if form.hint1.data and 'hint1' in new_hints:
            new_hints.remove('hint1')
        if form.hint2.data and 'hint2' in new_hints:
            new_hints.remove('hint2')
        if form.hint3.data and 'hint3' in new_hints:
            new_hints.remove('hint3')
        if form.hint4.data and 'hint4' in new_hints:
            new_hints.remove('hint4')
        if form.hint5.data and 'hint5' in new_hints:
            new_hints.remove('hint5')

        user.hints = new_hints  # Заменяем старый список новым
        db.session.commit()

    # Обработка нажатия на кнопки
    if form.validate_on_submit():
        # Проверяем, правильный ли ответ выбрал пользователь
        if form.answer.data and int(form.answer.data) == question.num_answer:
            # Пользователь выбрал правильный ответ, увеличиваем его выигрыш
            if level == 15:
                # Пользователь дошел до последнего уровня, перенаправляем на страницу завершения игры
                return redirect(url_for('end', level=level))
            else:
                session.pop("question_id")
                return redirect(url_for('question', level=level+1))
        else:
            # Пользователь выбрал неправильный ответ, перенаправляем на страницу завершения игры
            return redirect(url_for('end', level=level))

    print(user.hints)
    return render_template('question.html', form= form,
                            question= question.question, level= level,
                            rating= rating, hints= user.hints)


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
