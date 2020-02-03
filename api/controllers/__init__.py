from flask_restplus import Api
from .users import api as users_api
from .email_list import api as email_list_api
from .auth import api as auth_api
from .role import api as role_api
from .calendar import api as calendar_api
from .reporting import api as reporting_api
from .payment import api as payment_api
from .config import api as config_api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
    }
}

api = Api(
    title='Otter Pond Web API',
    version='0.0.1',
    description='Web API for the Otter Pond',
    authorizations=authorizations,
    security='apikey',
)

api.add_namespace(users_api, path="/users")
api.add_namespace(email_list_api, path="/email_lists")
api.add_namespace(auth_api, path="/auth")
api.add_namespace(role_api, path="/roles")
api.add_namespace(calendar_api, path="/calendar")
api.add_namespace(reporting_api, path="/reporting")
api.add_namespace(config_api, path="/config")
api.add_namespace(payment_api, path="/payment")


@api.errorhandler(Exception)
def handle_exception(error):
    '''This is a custom error'''
    print("ERROR HANDLER CALLED: ", error)
    return {'error': "Error processing request: " + error.message}, 400