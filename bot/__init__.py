from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    if test_config is None:
        if app.config['ENV'] == 'production':
            app.config.from_object('config.config.ProductionConfig')
        else:
            app.config.from_object('config.config.DevelopmentConfig')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app
