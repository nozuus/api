from flask_restplus import fields, Model

calendar_config_model = Model("CalendarConfig", {
    'type': fields.String,
    'api_key': fields.String,
    'calendar_url': fields.String,
})

