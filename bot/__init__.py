from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if app.config['ENV'] == 'production':
        app.config.from_object('config.config.ProductionConfig')
    else:
        app.config.from_object('config.config.DevelopmentConfig')

    return app
