import os
from flask_bcrypt import Bcrypt
from flask_mail import Mail

from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_user import roles_required
from sqlalchemy import create_engine, MetaData
from flask_blogging import SQLAStorage, BloggingEngine
from flask import Flask, render_template, redirect, url_for,flash,request, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_blogging.forms import RegistrationForm, LoginForm



from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ffb8d3c4534343110e9479fc06d5b929'
app.config["BLOGGING_URL_PREFIX"] = "/blog"
app.config["BLOGGING_DISQUS_SITENAME"] = "test"
app.config["BLOGGING_SITEURL"] = "http://Blogflask-env.eba-pdyg36za.us-east-2.elasticbeanstalk.com"
app.config["BLOGGING_SITENAME"] = "/My Site"
app.config["BLOGGING_KEYWORDS"] = ["blog", "meta", "keywords"]
app.config["FILEUPLOAD_IMG_FOLDER"] = "fileupload"
app.config["FILEUPLOAD_PREFIX"] = "/fileupload"
app.config["FILEUPLOAD_ALLOWED_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif"]

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres+psycopg2://postgres:" + "2655e0d4397dc758acfbbbfff348ede2" + "@db-blog-flask.cj90pgpw0d5w.us-east-2.rds.amazonaws.com";

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')


# Flask-Mail SMTP server settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_USERNAME = 'email@example.com'
MAIL_PASSWORD = 'password'
MAIL_DEFAULT_SENDER = '"MyApp" <noreply@example.com>'

# Flask-User settings
USER_APP_NAME = "Flask-User Basic App"  # Shown in and email templates and page footers
USER_ENABLE_EMAIL = True  # Enable email authentication
USER_ENABLE_USERNAME = False  # Disable username authentication
USER_EMAIL_SENDER_NAME = USER_APP_NAME
USER_EMAIL_SENDER_EMAIL = "noreply@example.com"


# Criei uma variável pass, caso não funcione substituir na linha do engine
passw = "2655e0d4397dc758acfbbbfff348ede2"

# extensions
# engine = create_engine('postgresql:////tmp/blog.db')
# engine = create_engine('sqlite:////tmp/blog.db')



engine = create_engine("postgres+psycopg2://postgres:" + passw + "@db-blog-flask.cj90pgpw0d5w.us-east-2.rds.amazonaws.com")
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)

login_manager.login_view = 'login'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager.login_message_category = 'info'
mail = Mail(app)



class User(db.Model,UserMixin):
    __tablename__ = 'users';
    user_id = db.Column(db.Integer, primary_key=True);
    name = db.Column(db.String(80));
    email = db.Column(db.String(120));
    password = db.Column(db.String(60));



    def __init__(self, user_id):
        self.id = user_id


    def get_name(self):
        return self.id   # typically the user's name


# Create customized model view class
class MyModelView(sqla.ModelView):

    ##def is_accessible(self):
       ## return False

   # def is_accessible(self):
        #return login.current_user.is_authenticated
    edit_modal = True
    can_create = False

admin = Admin(app, name="Flask-Blogging", template_mode='bootstrap3')
Post = sql_storage.post_model
Tag = sql_storage.tag_model
#Users = sql_storage.user_model
admin.add_view(MyModelView(Post, db.session))
admin.add_view(MyModelView(Tag, db.session))
admin.add_view(MyModelView(User, db.session))

@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    return User(user_id)

######################################################################

@app.route("/")
def index():
    return redirect("/blog")


#@roles_required('admin')
@app.route("/admin")
def admin():
    return redirect("/admin")


@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/blog")


####################################################################


@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print(form.username.data)
        if sql_storage.validate_username(form.username.data):
            flash('Username already in use.','danger')
        elif sql_storage.validate_email(form.email.data):
            flash('Email already registered.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = sql_storage.regiter_user(form.username.data, form.email.data, hashed_password)
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user_login = sql_storage.user(form.email.data)
        user = User(user_login.user_id)

        if user and bcrypt.check_password_hash(user_login.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect("/blog")
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=True)

