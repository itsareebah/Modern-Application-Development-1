import os
from flask import Flask, Blueprint
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_restful import Resource, Api

app = None
api = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
        raise Exception("currently no production configuration")
    else:
        print("staring local development")
        app.config.from_object(LocalDevelopmentConfig)
        db.init_app(app)
        api = Api(app)
        app.app_context().push()
        return app, api


app, api = create_app()
app.secret_key = 'areebah'

from application.card_controllers import *
api.add_resource(DeckAPI, '/api/dashboard', '/api/dashboard/<string:deck_id>')
api.add_resource(CardAPI, '/api/dashboard/<string:deck_id>/<int:card_id>', '/api/dashboard/<string:deck_id>/card')
api.add_resource(ScoreAPI, '/api/dashboard/<string:deck_id>/score')
api.add_resource(CardReviewAPI, '/api/dashboard/<string:deck_id>/<int:card_id>/review')
api.add_resource(DeckReviewAPI, '/api/dashboard/<string:deck_id>/review' )

from application.controllers import *

if __name__ == "__main__" :
    app.run(host="0.0.0.0", debug=True, port=8080)
