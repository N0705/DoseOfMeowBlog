from flask import Blueprint, render_template, redirect, url_for, request, flash
from init import db, mail
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from functools import wraps
from flask_mail import Message
import secrets
auth = Blueprint("auth", __name__)



@auth.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!")
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/sign-up", methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists =  User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.',category='error')
        elif password1 != password2:
            flash('Password does not match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category = 'error')
        elif len(password1) <6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            # Generate and set verification token
            verification_token = generate_verification_token()
            new_user.verification_token = verification_token
            db.session.commit()

            # Send verification email
            subject = 'Email Verification'
            body = f'Click the following link to verify your email: {url_for("auth.verify_email", token=verification_token, _external=True)}'
            msg = Message(subject, recipients=[email], body=body)
            mail.send(msg)

            flash('User created! Please check your email for verification instructions.')
            return redirect(url_for('views.home'))


    return render_template("signup.html", user=current_user)

@auth.route("/verify-email/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token, email_verified=False).first()

    if user:
        user.email_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Email verified successfully!', category='success')
        login_user(user, remember=True)
        return redirect(url_for('views.home'))
    else:
        flash('Invalid verification token or email already verified.', category='error')
        return redirect(url_for('views.home'))

def generate_verification_token():
    return secrets.token_urlsafe(30)

def is_user_verified(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user and not current_user.email_verified:
            flash('Please verify your email to access this page.', category='error')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))