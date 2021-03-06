from email import message
from flask import Flask, render_template, make_response,request, flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_mail import Mail, Message
from wtforms import Form, IntegerField, BooleanField, StringField,EmailField, PasswordField, validators
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import mplcyberpunk
import base64
from io import BytesIO
import pandas as pd

#plt.style.use("cyberpunk")


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
        db.session.add(questions(1, "Theo b???n thi???t k??? c???a s???n ph???m n??m nay th??? n??o?",'radio'))
        db.session.add(answers(1, "Tuy???t ?????p"))
        db.session.add(answers(1, "B??nh th?????ng"))
        db.session.add(answers(1, "X???u"))            
        
        db.session.add(questions(2, "Theo b???n c???n th??m t??nh n??ng n??o?",'checkbox'))
        db.session.add(answers(2, "Camera xuy??n th???u"))
        db.session.add(answers(2, "S???c si??u nhanh 1000w"))
        db.session.add(answers(2, "Pin dung l?????ng x5")) 
        db.session.add(answers(2, "Ram 50GB"))
        
        db.session.add(questions(3, "B???n th???y gi?? b??n h???p l?? kh??ng?",'radio'))
        db.session.add(answers(3, "?????t"))
        db.session.add(answers(3, "H???p l??"))
        db.session.add(answers(3, "R???"))
        
        db.session.commit()
    
    app.config['MAIL_SERVER']='mx.vitan.dev'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'no-reply@mail.vitan.dev'
    app.config['MAIL_PASSWORD'] = '17252101'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    class RegistrationForm(Form):
        name = StringField(label='Name', validators=[validators.DataRequired(message="Name is required.")])
        age = IntegerField(label='Age', validators=[validators.DataRequired(message="Age is required.")])
        jobTitle = StringField(label='Job Title', validators=[validators.DataRequired(message="Job Title is required.")])
        email = EmailField(
            label='Email', 
            validators=[
                validators.DataRequired(message="Email is required.")
                ]
            )
        phone = StringField(label='Phone', validators=[validators.DataRequired( message="Phone is required."), validators.Length(10, message="Phone must be 10-nunmber length.")])
    
    @app.route("/", methods=["GET","POST"])
    def index():
        listQuestions = questions.query.all()
        listAnswers = answers.query.all()        
        form = RegistrationForm(request.form)
        if(request.method=="POST"):
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
                msg = Message('C???m ??n b???n ???? tham gia kh???o s??t!', sender = 'no-reply@mail.vitan.dev', recipients = [email])
                msg.body = "C???m ??n b???n ???? tham gia kh???o s??t!"
                mail.send(msg)
                return redirect(url_for('thankyou', id=user.id))
        else:
            flash('L???i tung to??t, nh???p l???i ??i!', 'error')
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