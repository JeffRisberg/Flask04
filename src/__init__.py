import os
from dynaconf import FlaskDynaconf
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session

db = SQLAlchemy()
metadata = None
engine = None
coach = None


def create_app(secret_key):
	"""Initialize the Flask app instance"""
	global metadata
	global engine
	global coach

	# create the flask app instance
	app = Flask(__name__)
	app.secret_key = secret_key
	FlaskDynaconf(app)

	with app.app_context():
		app.config["SESSION_PERMANENT"] = True
		app.config["SESSION_TYPE"] = "filesystem"
		app.config["SESSION_COOKIE_SECURE"] = False
		app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
		Session(app)

		# initialize the database connection
		db_host = app.config['db_host']
		db_port = app.config['db_port']
		db_name = app.config['db_name']
		db_user = app.config['db_user']
		db_password = app.config['db_password']

		connect_str = "mysql+mysqlconnector://" + db_user + ":" + db_password + "@" + db_host + ":" + db_port + "/" + db_name
		print(connect_str)
		app.config['SQLALCHEMY_DATABASE_URI'] = connect_str

		# initialize plugins
		db.init_app(app)

		engine = db.create_engine(connect_str, engine_opts={})
		conn = engine.connect()

		metadata = db.MetaData()
		metadata.reflect(bind=conn)

		from . import routes

		return app
