from flask_admin import Admin
from website.models import User, Post, Favorite
from website import db
from website import create_app
from website.auth import AdminModelView


app = create_app()


# The admin for the site
admin = Admin(app)
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Post, db.session))
admin.add_view(AdminModelView(Favorite, db.session))


if __name__ == '__main__':
    app.run(debug=True)