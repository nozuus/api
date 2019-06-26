from flask import Flask
from .controllers import api
from flask_jwt_extended import JWTManager
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api.init_app(app)

app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET")
jwt = JWTManager(app)


@jwt.invalid_token_loader
def invalid_token(expired_token):
    token_type = expired_token['type']
    return {
        'status': 401,
        'msg': 'The {} token is invalid'.format(token_type)
    }, 401


@jwt.unauthorized_loader
def unauthorized(expired_token):
    token_type = expired_token['type']
    return {
        'status': 401,
        'msg': 'The {} token is invalid'.format(token_type)
    }, 401


if __name__ == "__main__":
	app.run(debug=True)