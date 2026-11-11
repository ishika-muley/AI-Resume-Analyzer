"""Flask application factory."""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.api import api

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config: app.config.update(config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    CORS(app)
    db.init_app(app)
    app.register_blueprint(api)
    with app.app_context(): db.create_all()
    @app.errorhandler(413)
    def too_large(_): return jsonify({"error": "File too large. Maximum size is 5 MB."}), 413
    @app.errorhandler(500)
    def server(_): return jsonify({"error": "Internal server error."}), 500
    return app

if __name__ == "__main__":
    create_app().run(port=5001, debug=True)
