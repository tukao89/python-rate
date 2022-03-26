FROM --platform=linux/amd64 python:3.8-slim

WORKDIR /app
COPY . .

ENV SECRET_KEY=123456
ENV SQLALCHEMY_DATABASE_URI=sqlite:////rate.db
ENV SQLALCHEMY_TRACK_MODIFICATIONS=False


RUN pip install -r requirements.txt

#RUN flask db init
#RUN flask db migrate
#RUN flask db upgrade

CMD waitress-serve --listen 0.0.0.0:$PORT wsgi:application