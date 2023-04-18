import random

from exts import db
from datetime import datetime


class EmailCaptchaModel(db.Model):
    __tablename__ = "email_captcha"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    captcha = db.Column(db.String(10), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    nickname = db.Column(db.String(100), unique=True)
    answer_times = db.Column(db.Integer, default=0)
    liked_times = db.Column(db.Integer, default=0)
    gravatar = db.Column(db.String(2000), default='./static/images/brand/ustc头头.jpg')
    idiom = db.Column(db.String(100), default='')
    follow = db.Column(db.Integer, default=0)
    followed = db.Column(db.Integer, default=0)
    anonymous_avatar_1 = db.Column(db.Integer, default=random.randint(0, 42))
    anonymous_avatar_2 = db.Column(db.Integer, default=random.randint(0, 13))
    anonymous_avatar_3 = db.Column(db.Integer, default=random.randint(0, 13))


class QuestionModel(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1200), nullable=False, default="暂无描述哦")
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("UserModel", backref="questions")
    comments = db.Column(db.Integer, default=0)


class AnswerModel(db.Model):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    question = db.relationship("QuestionModel", backref=db.backref("answers", order_by=create_time.desc()))
    author = db.relationship("UserModel", backref="answers")
    likes = db.Column(db.Integer, default=0)
    reply_id = db.Column(db.Integer, default=0)


class FollowModel(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class BlogModel(db.Model):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("UserModel", backref="blogs")
    likes = db.Column(db.Integer, default=0)
    collects = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)


class BlogLikesModel(db.Model):
    __tablename__ = "bloglikes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    blog = db.Column(db.Integer, db.ForeignKey('blog.id'), primary_key=True)


class BlogCollectionModel(db.Model):
    __tablename__ = "blogcollection"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    blog = db.Column(db.Integer, db.ForeignKey('blog.id'), primary_key=True)
    collector = db.relationship("UserModel", backref='collectors')
    create_time = db.Column(db.DateTime, default=datetime.now)


class CommentLikeModel(db.Model):
    __tablename__ = "commentlike"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer = db.Column(db.Integer, db.ForeignKey('answer.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)


class CommentModel(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    blog = db.relationship("BlogModel", backref=db.backref("comments_", order_by=create_time.desc()))
    author = db.relationship("UserModel", backref="comments_")
    likes = db.Column(db.Integer, default=0)

