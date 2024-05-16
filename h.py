# from app import app, db
# from app.models import Question
# import sqlalchemy as sa

# app.app_context().push()

# with open("questions.txt") as file:
#     loading = 0

#     for line in file:
#         question, answer1, answer2, answer3, answer4, num_answer, level = \
#             line.strip().strip("\ufeff").split("\t")
        
#         if level != loading:
#             loading = level
#             print(f"Начинаю загрузу {loading}")
        
#         q = Question(question= question, answer_1= answer1, answer_2= answer2,\
#                      answer_3= answer3, answer_4= answer4, num_answer= num_answer,\
#                      level= level)
#         db.session.add(q)
        
# db.session.commit()


rating = [3000000,1500000,800000,400000,200000,100000,50000,25000,15000,10000,5000,3000,2000,1000,500]
rating.reverse()
print(rating)
