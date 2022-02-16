from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    if request.method == 'POST':
        data = request.form
        is_valid_signup_data(data)
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


def is_valid_signup_data(data) -> None:
    """
    Check if the input entered by the user is legal and raise flash if not
    :param data: The request form of the input
    :return: None
    """
    email = data.get('email')
    first_name = data.get('firstName')
    password1 = data.get('password1')
    password2 = data.get('password2')
    if password1 != password2:
        flash('Passwords don\'t match.', category='error')
        print("Eee")

    elif len(email) < 4:
        flash('Email must be at least 4 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be at least 2 characters.', category='error')
    elif password1 != password2:
        flash('Passwords don\'t match.', category='error')
    elif len(password1) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        flash('Your account has been created successfully!', category='success')