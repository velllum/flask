from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)

"""BREADCRUMBS"""
from flask_breadcrumbs import Breadcrumbs
breadcrumbs = Breadcrumbs()
breadcrumbs.init_app(app)

"""SEARCH"""
from flask_msearch import Search
search = Search()
search.init_app(app)



