from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.datastructures import ImmutableMultiDict
from flask_admin.contrib.sqla import ModelView
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from typing import Tuple, Union
import random
import string

ADMIN_EMAIL = "nirblo50@gmail.com"
auth = Blueprint('auth', __name__)
HASH_METHOD = 'sha256'


class AdminModelView(ModelView):
    """
    This class is the view page of the admin
    """

    def is_accessible(self):
        """ Lets only the user logged in to admin user to see admin menu """
        if current_user.is_authenticated:
            return current_user.email == ADMIN_EMAIL
        return False

    def inaccessible_callback(self, name, **kwargs):
        """ Show unauthorized user forbidden page """
        return "<h1> Forbidden </h1>"


@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up() -> str:
    """
    The sign-up user page, receives user's information form, validate it and
    if it is valid saves the user to the DB and login the user to system
    :return: HTML page for home if the input is valid else sign-up HTML page
    """
    if request.method == 'POST':  # Client has sent a form
        data = request.form
        if is_valid_signup_data(data):
            user = create_new_user(data)
            flash('Your account has been created successfully!',
                  category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", sign_up="active", user=current_user)


@auth.route('/login', methods=["GET", "POST"])
def login() -> str:
    """"
    The login user page, receives user's information form, validate it and
    if it is valid logins the user to system
    :return: HTML page for home if the input is valid else login HTML page
    """
    if request.method == 'POST':  # Client has sent a form
        email, password = request.form.get('email'), request.form.get(
            'password')
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


@auth.route('/guest_login')
def guest_login() -> str:
    """
    Creates a new guest user
    """
    guests = User.query.filter_by(first_name="Guest").all()
    guest_id = max([user.id for user in guests]) + 1 if guests else 1
    guest = {"email": f"guest{guest_id}@guest.com",
             "firstName": "Guest",
             "password1": generate_password(password_len=7)}
    new_guest = create_new_user(guest)
    new_guest.notifications = False

    login_user(new_guest, remember=True)
    db.session.commit()
    flash(f'Logged in successfully!, Hello Guest',
          category='success')
    return redirect(url_for('views.home'))


@auth.route('/logout')
@login_required
def logout() -> str:
    """
    Logs the user out of the system and reroute to the login page
    :return: login HTML page
    """
    logout_user()
    return redirect(url_for('auth.login'))


def is_valid_signup_data(data: ImmutableMultiDict[str, str]) -> bool:
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

    if user:  # If user with this email is in the DB
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


def is_valid_login(user: Union[User, None], password: str) -> Tuple[bool, str]:
    """
    Receive user and password and return True if a user with the same
    email and password exist in the DB or False if not
    :param user: User type with the email given or None if no such email found
    :param password: The password the user has given
    """
    if user:  # If such email exist
        if check_password_hash(user.password, password):
            return True, user.first_name
        else:
            return False, "Incorrect password"
    return False, "No such email"


def create_new_user(data: ImmutableMultiDict[str, str]) -> User:
    """
    Creates new user in our DB
    :param data: The request form of the user input
    :return: None
    """
    email = data.get('email')
    first_name = data.get('firstName')
    password1 = data.get('password1')

    new_user = User(email=email, first_name=first_name,
                    password=
                    generate_password_hash(password1, method=HASH_METHOD),
                    notifications=True)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def generate_password(password_len) -> str:
    """
    Generates a new random password
    :return: random password
    """
    options = string.ascii_lowercase + '123456789'
    password = ''.join(random.choice(options) for i in range(password_len))
    return password
