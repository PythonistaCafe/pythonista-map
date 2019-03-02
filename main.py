import os
from flask import Flask
from waitress import serve


def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'map.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    # print('app config: ', app.config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'here will come the map later'

    import map  # from . import map
    app.register_blueprint(map.bp)
    app.add_url_rule('/', endpoint='index')

    import db  # from . import db
    db.init_app(app)

    return app


if __name__ == '__main__':
    serve(create_app(), host='0.0.0.0', port=5000)
