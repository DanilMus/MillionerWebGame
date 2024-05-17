from flask import render_template, redirect, url_for
from flask import session, request

from sqlalchemy.sql.expression import func
import random

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
            user.hints = new_hints  # Заменяем старый список новым
            db.session.commit()
            votes = [random.randint(0, 100) for _ in range(4)] # Формируем список со случайными голосами
            return render_template('question.html', form= form,
                                    question= question.question, level= level,
                                    rating= rating, votes= votes)
        
        # hint2 - 50 на 50
        if form.hint2.data and 'hint2' in new_hints:
            new_hints.remove('hint2')
            # Создаем список всех вариантов ответов
            all_answers = [1, 2, 3, 4]
            # Удаляем правильный ответ из списка
            all_answers.remove(question.num_answer)
            # Выбираем случайный неправильный ответ для удаления
            wrong_answer_to_remove = random.choice(all_answers)
            # Создаем новый список ответов, содержащий только правильный ответ и один неправильный ответ
            new_answers = [question.num_answer, wrong_answer_to_remove]
            # Обновляем варианты ответов в форме
            form.answer.choices = [(num, getattr(question, f'answer_{num}')) for num in new_answers]
            db.session.commit()

        # hint3 - Звонок другу
        if form.hint3.data and 'hint3' in new_hints:
            new_hints.remove('hint3')
            user.hints = new_hints
            db.session.commit()
            # Генерируем случайный номер телефона
            phone_number = "+7 " + ''.join(random.choice('0123456789') for _ in range(10))
            return render_template('phone_call.html', phone_number= phone_number, level= level)

        # hint4 - Право на ошибку
        if form.hint4.data and 'hint4' in new_hints:
            new_hints.remove('hint4')
            session['second_chance'] = True

        # hint5 - Замена вопроса 
        if form.hint5.data and 'hint5' in new_hints:
            new_hints.remove('hint5')
            question = Question.query.filter_by(level=level).order_by(func.random()).first()
            session['question_id'] = question.id

        user.hints = new_hints  # Заменяем старый список новым
        db.session.commit()

    # Обработка нажатия на кнопки "Ответить"
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
        # Пользователь выбрал неправильный ответ
        elif 'second_chance' in session:
            # Пользователь использовал подсказку "Право на ошибку", перезагружаем страницу
            session.pop('second_chance')
            return redirect(url_for('question', level=level))
        else:
            # Пользователь выбрал неправильный ответ, перенаправляем на страницу завершения игры
            return redirect(url_for('end', level=level))


    
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
