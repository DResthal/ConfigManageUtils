import logging
from flask import Flask
from flask_migrate import Migrate
import os
from .log import CustomLogger


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    if test_config is not None:
        app.config.from_object(test_config)
    else:
        try:
            app.config.from_pyfile("config.py")
        except:
            pass

    # Instance directory and logging setup
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    log_dir = os.path.join(app.instance_path, "logs/")

    try:
        os.makedirs(log_dir)
    except OSError:
        pass

    error_formatter = """%(asctime)s %(levelname)s: %(filename)s %(lineno)d
        %(message)s"""

    err_log = CustomLogger(
        name="elog",
        log_file=os.path.join(log_dir, "error.log"),
        level=logging.WARNING,
        formatter=logging.Formatter(error_formatter),
    ).create_logger()

    # Application setup
    with app.app_context():
        from .extensions import db, ma
        from .params.routes import params

        app.register_blueprint(params)
        migrate = Migrate(app, db)
        db.init_app(app)
        ma = ma.init_app(app)

        @app.route("/sanitycheck", methods=["GET"])
        def test():
            err_log.warning(
                "Sanity check route accessed. Application is running! If you see this, the application and error log is working correctly."
            )
            return "Working", 200

        return app
