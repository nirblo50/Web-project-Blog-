from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from typing import Tuple

auth = Blueprint('auth', __name__)
HASH_METHOD = 'sha256'


@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    if request.method == 'POST':
        data = request.form
        if is_valid_signup_data(data):
            user = create_new_user(data)
            flash('Your account has been created successfully!',
                  category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", sign_up="active", user=current_user)


@auth.route('/login', methods=["GET", "POST"])
def login():
    """
    The login user paige
    :return: The http of the login page
    """
    if request.method == 'POST':
        email, password = request.form.get('email'), request.form.get('password')
        user = User.query.filter_by(email=email).first()
        is_valid, message = is_valid_login(user, password)
        if is_valid:
            flash(f'Logged in successfully!, Hello {message}',
                  category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash(message, category='error')

    return render_template("login.html", login="active", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def is_valid_signup_data(data) -> bool:
    """
    Check if the input entered by the user is legal and raise flash if not
    :param data: The request form of the user input
    :return: True if legal data or False if not
    """
    email = data.get('email')
    first_name = data.get('firstName')
    password1 = data.get('password1')
    password2 = data.get('password2')

    user = User.query.filter_by(email=email).first()

    if user:    # If user with this email is in the DB
        flash('Email already exists.', category='error')

    elif password1 != password2:
        flash('Passwords don\'t match.', category='error')

    elif len(email) < 4:
        flash('Email must be at least 4 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be at least 2 characters.', category='error')
    elif password1 != password2:
        flash('Passwords don\'t match.', category='error')
    elif len(password1) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        return True
    return False


def is_valid_login(user, password) -> Tuple[bool, str]:
    """
    Receive user email and password and return True if a user with the same
    email and password exist in the DB or False if not
    :param email: The email the user has passed
    :param password: The password the user has passed
    """

    if user:    # If such email exist
        if check_password_hash(user.password, password):
            return True, user.first_name
        else:
            return False, "Incorrect password"
    return False, "No such email"


def create_new_user(data) -> User:
    """
    Creates new user in our DB
    :param data: The request form of the user input
    :return: None
    """
    email = data.get('email')
    first_name = data.get('firstName')
    password1 = data.get('password1')

    new_user = User(email=email, first_name=first_name,
                    password=generate_password_hash(
                        password1, method=HASH_METHOD))
    db.session.add(new_user)
    db.session.commit()
    return new_user
