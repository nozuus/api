from flask_restplus import fields, Model

subscribe_model = Model("SubscribeToList", {
    'user_id': fields.String,
})


list_model = Model("EmailList", {
    "prefix": fields.String,
    "domain": fields.String,
    "subject_prefix": fields.String
})


get_list_model = Model.inherit("GetEmailList", list_model, {
    "list_id": fields.String
})