from flask import Blueprint, render_template, redirect, url_for, request, \
    flash
from flask_login import login_required, current_user
from .models import Post, User, Favorite
from . import db
from email_sender import send_email
from website.auth import ADMIN_EMAIL
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
    user_favorites_id = [fav.post_id for fav in current_user.favorites]
    return render_template("home.html", home="active", user=current_user,
                           posts=posts, user_favorites_id=user_favorites_id,
                           ADMIN_EMAIL=ADMIN_EMAIL)


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
            flash('your post has been published', category='success')
            send_post_to_all(new_post)

    posts = Post.query.all()
    return render_template("new_post.html", posts_active="active",
                           user=current_user, posts=posts)


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

    user_favorites_id = [fav.post_id for fav in user.favorites]
    posts = user.posts
    return render_template("user_posts.html", user=current_user, posts=posts,
                           email=email, first_name=user.first_name,
                           user_favorites_id=user_favorites_id)


@views.route("/profile/<email>", methods=["GET", "POST"])
@login_required
def profile(email):
    """
    The Page for user profile with all his personal information
    :param email: The user's email
    :return: HTML page of the profile
    """
    num_posts = len(current_user.posts)
    return render_template("profile.html", profile="active", email=email,
                           user=current_user, num_posts=num_posts)


@views.route("/favorites")
@login_required
def favorites():
    """
    The Page of all the posts a certain user had flagged favorites
    :return: HTML page of the favorites
    """
    user_favorites_id = [fav.post_id for fav in current_user.favorites]
    posts = Post.query.filter(
        Post.id.in_(user_favorites_id)).all()

    return render_template("favorites.html",
                           user=current_user, posts=posts, favorites="active",
                           email=current_user.email,
                           first_name=current_user.first_name,
                           user_favorites_id=user_favorites_id)


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
    elif current_user.id != post.author and current_user.email != ADMIN_EMAIL:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/flag-favorite/<post_id>")
@login_required
def flag_as_favorite(post_id: str) -> str:
    """
    Flags a Post as favorite for the user who asked
    :param post_id: The Id of the post to flag
    :return: html page of the home page
    """
    favorite = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if not favorite:    # If user hasn't flagged this post
        new_favorite = Favorite(user_id=current_user.id, post_id=post_id)
        db.session.add(new_favorite)
        db.session.commit()
    else:
        db.session.delete(favorite)
        db.session.commit()
        return redirect(url_for('views.favorites'))
    return redirect(url_for('views.home'))


def send_post_to_all(post: Post) -> None:
    """
    Send an email with a new post to all users
    :param post: The new post
    :return: None
    """
    users = User.query.all()
    post_writer = User.query.filter_by(id=post.author).first()
    writer_name = post_writer.first_name

    for user in users:
        if user.notifications:  # If user is subscribed to notifications
            send_email(user.email, f"New Post Published by {writer_name}"
                       , f"{post_writer.email} has posted: \n{post.text}",
                       "By, Nir Balouka \n\n\n" +
                       "You can unsubscribe in the link:\n" +
                       "https://nirblo50.pythonanywhere.com/subscription/unsubscribe")