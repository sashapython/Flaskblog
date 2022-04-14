from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "nou"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

from flaskblog import urls