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

jwt._set_error_handler_callbacks(api)


@jwt.invalid_token_loader
def invalid_token(reason):
    return {
        'status': 401,
        'msg': 'Invalid Token. Reason: %s' % reason
    }, 401


@jwt.unauthorized_loader
def unauthorized(reason):
    return {
        'status': 401,
        'msg': 'Invalid Token. Reason: %s' % reason
    }, 401



if __name__ == "__main__":
	app.run(debug=True)