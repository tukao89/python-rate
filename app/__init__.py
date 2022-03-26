from flask import Flask, render_template, make_response,request, flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_mail import Mail, Message
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import mplcyberpunk
import base64
from io import BytesIO
import pandas as pd

plt.style.use("cyberpunk")


def create_app():
    
    app = Flask(__name__)
    app.secret_key = '1234567890'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.instance_path}/rate.sqlite3'

    db = SQLAlchemy(app)
    
    class users(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        name = db.Column(db.String(1000))        
        age = db.Column(db.Integer)
        jobTitle = db.Column(db.String(1000))
        email = db.Column(db.String(1000))
        phone = db.Column(db.String(1000))
    
        def __init__(self, name, age, jobTitle, email, phone):
            self.name = name
            self.age = age
            self.jobTitle = jobTitle
            self.email = email
            self.phone = phone
        
    class questions(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        question = db.Column(db.String(1000))        
        type = db.Column(db.String(20))        
    
        def __init__(self, id, question, type):
            self.id = id
            self.question = question
            self.type = type
    
    class answers(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        questionId = db.Column(db.Integer)        
        answer = db.Column(db.String(1000))
    
        def __init__(self, questionId, answer):
            self.questionId = questionId
            self.answer = answer
    
    class userAnswers(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        userId = db.Column(db.Integer)        
        questionId = db.Column(db.Integer)        
        answerId = db.Column(db.Integer)
     
        def __init__(self,userId, questionId, answerId):
            self.userId = userId
            self.questionId = questionId
            self.answerId = answerId
   
    db.create_all()
    
    if questions.query.first() is None:
        db.session.add(questions(1, "Theo bạn thiết kế của sản phẩm năm nay thế nào?",'radio'))
        db.session.add(answers(1, "Tuyệt đẹp"))
        db.session.add(answers(1, "Bình thường"))
        db.session.add(answers(1, "Xấu"))            
        
        db.session.add(questions(2, "Theo bạn cần thêm tính năng nào?",'checkbox'))
        db.session.add(answers(2, "Camera xuyên thấu"))
        db.session.add(answers(2, "Sạc siêu nhanh 1000w"))
        db.session.add(answers(2, "Pin dung lượng x5")) 
        db.session.add(answers(2, "Ram 50GB"))
        
        db.session.add(questions(3, "Bạn thấy giá bán hợp lý không?",'radio'))
        db.session.add(answers(3, "Đắt"))
        db.session.add(answers(3, "Hợp lý"))
        db.session.add(answers(3, "Rẻ"))
        
        db.session.commit()
    
    app.config['MAIL_SERVER']='mx.vitan.dev'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'no-reply@mail.vitan.dev'
    app.config['MAIL_PASSWORD'] = '17252101'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    class RegistrationForm(Form):
        name = StringField('Name', [validators.DataRequired(message="Name is required.")])
        age = StringField('Age', [validators.DataRequired(message="Age is required.")])
        jobTitle = StringField('Job Title', [validators.DataRequired(message="Job Title is required.")])
        email = StringField("Email",  [validators.DataRequired(message="Email is required."), validators.Email("This ~field requires a valid email address")])
        phone = StringField('Phone')
        password = PasswordField('New Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords must match')])
        confirm = PasswordField('Repeat Password')
    
    
    @app.route("/test-mail")
    def testMail():
        msg = Message('Hello', sender = 'no-reply@mail.vitan.dev', recipients = ['tu.phunganh@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        return "Sent"
    
    @app.route("/", methods=["GET","POST"])
    def index():
        listQuestions = questions.query.all()
        listAnswers = answers.query.all()        
        form = RegistrationForm(request.form)
        if(request.method=="POST") :
            name = request.form.get("name")
            age = request.form.get("age")
            jobTitle = request.form.get("jobTitle")
            email = request.form.get("email")
            phone = request.form.get("phone")
            user = users(name,age,jobTitle,email,phone)
            db.session.add(user)            
            db.session.commit()            
            if user.id>0:
                for q in listQuestions:
                    if request.form.get("q"+str(q.id)):
                        for val in request.form.getlist("q"+str(q.id)):
                            db.session.add(userAnswers(user.id, q.id,val))
                db.session.commit()
                return redirect(url_for('thankyou', id=user.id))
        else:
            flash('Lỗi tung toét, nhập lại đi!', 'error')
        return render_template("index.html", form = form, questions=listQuestions, answers=listAnswers)
    
    @app.route("/thankyou/<int:id>")
    def thankyou(id):        
        listQuestions = questions.query.all()
        listAnswers = answers.query.all()        
        listUserAnswers = userAnswers.query.all()    
       
        charts = []
        for q in listQuestions:
            fig, ((ax3)) = plt.subplots(1, 1, constrained_layout=False, figsize=(5, 5), dpi=100)
            #data = get_answer_by_question(q.id)
            answ = {}
            for a in listAnswers:                
                if a.questionId==q.id:
                    answ[a.answer] = 0
                    for ans in listUserAnswers:
                        if ans.questionId == q.id and ans.answerId==a.id:
                            answ[a.answer] = answ[a.answer] + 1
            
        #df = pd.DataFrame(result)
        #plot = df.plot.pie(subplots=True, figsize=(11, 6))           

            ax3.set_title(q.question, fontsize=11)

            #
            labels = answ.keys()
            values = answ.values()
            explode = []
            for item in answ.keys():
                explode.append(0.01)

            ax3.pie(values, labels=labels, autopct="%.2f%%", explode=explode)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            charts.append(data)
            print(answ)
        return render_template("thankyou.html",id=id, charts=charts)

    def get_answer_by_question(questionId):
        query = db.session.query(
            questions.question,
            questions.id,            
            answers.id,
            answers.answer,
            userAnswers.answerId
        ).filter(questions.id==questionId)
        return query.all()
    
    return app