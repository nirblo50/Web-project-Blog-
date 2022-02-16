from flask import Blueprint, render_template, request

auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    data = request.form
    return render_template("sign_up.html", sign_up="active")


@auth.route('/login', methods=["GET", "POST"])
def login():
    """
    The login user paige
    :return: The http of the login page
    """
    data = request.form
    return render_template("login.html", login="active")


@auth.route('/logout')
def logout():
    return render_template("logout.html", logout="active")
