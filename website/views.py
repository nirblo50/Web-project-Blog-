from flask import Blueprint, render_template, redirect, url_for, request, \
    flash
from flask_login import login_required, current_user
from .models import Post, User
from . import db
from email_sender import send_email

views = Blueprint('views', __name__)


@views.route('/')
def default() -> str:
    """
    Default landing page, reroutes to the home page if the user is connected
    to the system, else reroutes to the login page
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    else:
        return redirect(url_for('auth.login'))


@views.route('/home', methods=["GET", "POST"])
@login_required
def home() -> str:
    """
    Default landing page, reroutes to the home page if the user is connected
    to the system, else reroutes to the login page
    :return:
    """
    posts = Post.query.all()
    return render_template("home.html", home="active", user=current_user,
                           posts=posts)


@views.route('/posts', methods=["GET", "POST"])
@login_required
def new_post() -> str:
    """
    Home page, handles user's notes
    :return: HTML home page
    """
    if request.method == 'POST':    # Client has sent a form
        text = request.form.get('text')

        if len(text) < 1:
            flash('Note is too short!', category='error')
        else:
            new_post = Post(text=text, author=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Note added!', category='success')
            send_post_to_all(new_post)

    posts = Post.query.all()
    return render_template("new_post.html", posts_active="active", user=current_user, posts=posts)


@views.route("/user_posts/<email>")
@login_required
def user_posts(email):
    """
    The Page of all the posts a certain user had posted
    :param email: The email of the user to show all his posts
    :return: HTML page of the user_posts
    """
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('No user with that email exists.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=user.id).all()
    return render_template("user_posts.html", user=current_user, posts=posts, email=email, first_name=user.first_name)


@views.route("/profile/<email>", methods=["GET", "POST"])
@login_required
def profile(email):
    """
    The Page for user profile with all his personal information
    :param email: The user's email
    :return: HTML page of the profile
    """
    num_posts = len(current_user.posts)
    return render_template("profile.html", profile="active", email=email ,user=current_user, num_posts=num_posts)


@views.route("/subscription/<subscribe>", methods=["GET", "POST"])
@login_required
def subscribe(subscribe):
    """
    Url for subscription/unsubscription to email notifications
    :param subscribe: subscription/subscription
    :return: Redirect to user profile Page
    """
    if subscribe == "subscribe":
        current_user.notifications = True
        db.session.commit()
        flash('You have subscribed successfully', category='success')
    elif subscribe == "unsubscribe":
        current_user.notifications = False
        db.session.commit()
        flash('You have unsubscribed successfully', category='success')

    return redirect(url_for('views.profile', email=current_user.email))


@views.route("/delete-post/<id>")
@login_required
def delete_post(id: str) -> str:
    """
    Deletes a Post with given id
    :param id: The Id of the post to delete
    :return: html page of the home page
    """
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


def send_post_to_all(post: Post) -> None:
    """
    Send an email with a new post to all users
    :param post: The new post
    :return: None
    """
    users = User.query.all()
    post_writer = User.query.filter_by(id=post.author).first()

    for user in users:
        if user.notifications:  # If user is subscribed to notifications
            send_email(user.email, f"New Post Published by {user.first_name}"
                       , f"{post_writer.email} has posted: \n{post.text}",
                       "By, Nir Balouka")