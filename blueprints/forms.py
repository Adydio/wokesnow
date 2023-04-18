import wtforms
from wtforms.validators import length, email, EqualTo, InputRequired
from models import EmailCaptchaModel, UserModel


class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[email()])
    password = wtforms.StringField(validators=[length(min=6, max=20)])


class RegisterForm(wtforms.Form):
    username = wtforms.StringField(validators=[length(min=1, max=20)])
    email = wtforms.StringField(validators=[email()])
    captcha = wtforms.StringField(validators=[length(min=6, max=6)])
    password = wtforms.StringField(validators=[length(min=8, max=20)])
    password_confirm = wtforms.StringField(validators=[EqualTo("password")])

    def validate_captcha(self, field):
        captcha = field.data
        email_ = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(email=email_).first()
        if not captcha_model or captcha_model.captcha != captcha:
            raise wtforms.ValidationError("邮箱验证码错误！")

    def validate_email(self, field):
        email_ = field.data
        user_model = UserModel.query.filter_by(email=email_).first()
        if user_model:
            raise wtforms.ValidationError("邮箱已经存在！")


class QuestionForm(wtforms.Form):
    title = wtforms.StringField(validators=[length(min=3, max=200)])
    content = wtforms.StringField(validators=[length(min=3, max=1200)])


class AnswerForm(wtforms.Form):
    content = wtforms.StringField(validators=[length(min=1)])


class changeForm(wtforms.Form):
    idiom = wtforms.StringField(validators=[length(min=0)])
    newusername = wtforms.StringField(validators=[length(min=1, max=10)])
