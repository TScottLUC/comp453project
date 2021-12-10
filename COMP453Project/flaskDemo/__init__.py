from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import yaml
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tps:password@localhost/covid'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

yamlDB = yaml.load(open('flaskDemo/db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = yamlDB['mysql_host']
app.config['MYSQL_USER'] = yamlDB['mysql_user']
app.config['MYSQL_PASSWORD'] = yamlDB['mysql_password']
app.config['MYSQL_DB'] = yamlDB['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

from flaskDemo import routes
from flaskDemo import models

models.db.create_all()
