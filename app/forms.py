# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo


class LoginForm(Form):
    email = StringField('Email Address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])


class RegisterForm(Form):
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Confirm password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )