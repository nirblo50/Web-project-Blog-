from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


MAX_LEN = 100


class Note(db.Model):
    """
    This class represents a note that users write and save to the DB
    """
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(MAX_LEN**2))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    """
    This class represents a user in the site
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(MAX_LEN), unique=True)
    password = db.Column(db.String(MAX_LEN))
    first_name = db.Column(db.String(MAX_LEN))
    notes = db.relationship('Note')
