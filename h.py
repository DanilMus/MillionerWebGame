from app import app, db
from app.models import Question
import sqlalchemy as sa

app.app_context().push()

with open("questions.txt") as file:
    loading = 0

    for line in file:
        question, answer1, answer2, answer3, answer4, num_answer, level = \
            line.strip().strip("\ufeff").split("\t")
        
        if level != loading:
            loading = level
            print(f"Начинаю загрузу {loading}")
        
        q = Question(question= question, answer_1= answer1, answer_2= answer2,\
                     answer_3= answer3, answer_4= answer4, num_answer= num_answer,\
                     level= level)
        db.session.add(q)
        
db.session.commit()


        