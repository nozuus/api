from flask_restplus import Api
from .users import api as users_api

api = Api(
    title='Nozuus Web API',
    version='0.0.1',
    description='Web API for Nozuus',
)

api.add_namespace(users_api, path="/users")
