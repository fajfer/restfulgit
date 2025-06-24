from datetime import timedelta

from flask import Flask

from restfulgit.archives import archives
from restfulgit.plumbing.routes import plumbing
from restfulgit.porcelain.routes import porcelain
from restfulgit.utils.json import jsonify
from restfulgit.utils.json_err_pages import (
    json_error_page,
    register_general_error_handler
)

BLUEPRINTS = (plumbing, porcelain, archives)

class DefaultConfig(object):
    RESTFULGIT_REPO_BASE_PATH = "/git/"
    RESTFULGIT_DEFAULT_COMMIT_LIST_LIMIT = 50

    RESTFULGIT_ENABLE_CORS = False
    RESTFULGIT_CORS_ALLOWED_ORIGIN = "*"
    RESTFULGIT_CORS_ALLOW_CREDENTIALS = False
    RESTFULGIT_CORS_ALLOWED_HEADERS = []
    RESTFULGIT_CORS_MAX_AGE = timedelta(days=30)

    DEBUG = False

def run():
    from waitress import serve

    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    register_general_error_handler(app, json_error_page)

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    @app.route("/")
    @jsonify
    def index():
        links = []
        for rule in app.url_map.iter_rules():
            if str(rule).startswith("/repos"):
                links.append(str(rule))
        return links

    serve(app, host='0.0.0.0', port=5000)
