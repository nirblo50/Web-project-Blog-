from flask import Blueprint, render_template, redirect, url_for, request, \
    flash
from flask_login import login_required, current_user
from .models import Post, User
from . import db

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