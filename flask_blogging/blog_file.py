
from flask import Flask, render_template_string, redirect
from sqlalchemy import create_engine, MetaData
from flask_blogging import SQLAStorage, BloggingEngine
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_blogging.forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ffb8d3c4534343110e9479fc06d5b929'
app.config["BLOGGING_URL_PREFIX"] = "/blog"
app.config["BLOGGING_DISQUS_SITENAME"] = "test"
app.config["BLOGGING_SITEURL"] = "http://localhost:8000"
app.config["BLOGGING_SITENAME"] = "/My Site"
app.config["BLOGGING_KEYWORDS"] = ["blog", "meta", "keywords"]
app.config["FILEUPLOAD_IMG_FOLDER"] = "fileupload"
app.config["FILEUPLOAD_PREFIX"] = "/fileupload"
app.config["FILEUPLOAD_ALLOWED_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif"]

# Criei uma variável pass, caso não funcione substituir na linha do engine
passw = "12345"

# extensions
# engine = create_engine('postgresql:////tmp/blog.db')
# engine = create_engine('sqlite:////tmp/blog.db')

engine = create_engine("postgres+psycopg2://postgres:" + passw + "@localhost/Blog")
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)

login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_name(self):
        return "Paul Dirac"  # typically the user's name


@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    return User(user_id)





@app.route("/")
def index():
    return redirect("/blog")


@app.route("/home")
def home():
    return render_template('home.html')

# Se quiser verificar a opção de CRUD do blog descomenta esta parte e comenta a parte login abaixo
#@app.route("/login/")
#def login():
    #user = User("testuser")
    #login_user(user)
    #return redirect("/blog")



@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)


@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=True)
