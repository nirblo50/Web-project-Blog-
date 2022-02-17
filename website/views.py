from flask import Blueprint, render_template, redirect, url_for, request, \
    flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

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
    Home page, handles user's notes
    :return: HTML home page
    """
    if request.method == 'POST':    # Client has sent a form
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", home="active", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    """
    Deletes a note
    """
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
