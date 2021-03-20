from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import (BooleanField, Form, PasswordField, StringField,
                     ValidationError, validators)
from wtforms.fields.html5 import EmailField

from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('auth/login.html', form=form)

@auth.route('/login', methods=['POST'])
def login_post():
    form = LoginForm(request.form)
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'is-danger')
        return render_template('auth/login.html', form=form)

    if not form.validate_on_submit():
        flash('An error occured. Please try again.', 'is-danger')
        return render_template('auth/login.html', form=form)

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

class LoginForm(FlaskForm):
    email = EmailField('Email Address', [
        validators.Email(),
        validators.DataRequired(),
    ])
    password = PasswordField('Password', [
        validators.InputRequired(),
    ])
    remember = BooleanField('Remember me')

@auth.route('/register')
def register():
    form = RegistrationForm(request.form)
    return render_template('auth/register.html', form=form)

@auth.route('/register', methods=['POST'])
def register_post():
    form = RegistrationForm(request.form)
    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('password')

    if form.validate_on_submit():
        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password, method='sha256'),
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=25),
    ])
    email = EmailField('Email Address', [
        validators.DataRequired(),
        validators.Email(message='Please enter a valide email address'),
        validators.Length(min=6, max=35),
    ])
    password = PasswordField('Password', validators = [
        validators.InputRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
    ])
    confirm = PasswordField('Confirm Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('A user with this email address already exists.')
