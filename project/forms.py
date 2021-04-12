from models import User
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    re_password = PasswordField('re_password', validators=[DataRequired()])


class LoginForm(FlaskForm):

    # 비밀번호 확인
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message

        def __call__(self, form, field):
            userid = form['userid'].data
            password = field.data

            user = User.query.filter_by(userid=userid).first()
            if user.password != password:
                raise ValueError('Wrong Password')


    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()])
