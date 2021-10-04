from flask import request, current_app
from logging import getLogger
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_basicauth import BasicAuth


e_log = getLogger("elog")

db = SQLAlchemy()
ma = Marshmallow()
basic_auth = BasicAuth()
