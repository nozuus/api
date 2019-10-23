from flask import request, Response
from flask_restplus import Namespace, Resource, fields
from api.models.calendar_model import calendar_config_model
import core.services.calendar_service as calendar_service
from flask_jwt_extended import jwt_required
import core.services.auth_services as auth_services


api = Namespace('calendar', description='Calendar related operations')

api.models[calendar_config_model.name] = calendar_config_model


@api.route("/config")
class CalendarConfigResource(Resource):
    @api.doc("set_calendar_config")
    @api.expect(calendar_config_model)
    @jwt_required
    def post(self):
        '''Set the active calendar configuration.'''
        body = request.json
        calendar_type = body["type"]
        api_key = body["api_key"]
        url = body["calendar_url"]
        result = calendar_service.set_configuration(calendar_type, api_key, url)
        if result is not False:
            return {"error": "Success"}
        return {"error": "Unable to set calendar configuration"}

    @api.doc("get_calendar_config")
    @api.marshal_with(calendar_config_model)
    @jwt_required
    def get(self):
        '''Get the active calendar configuration'''
        config = calendar_service.get_configuraiton()
        if config:
            return config
        return {"error" : "Unable to retrieve calendar configuration"}


@api.route("/generateLink")
class CalendarConfigResource(Resource):
    @api.doc("generate_user_ics_link")
    @jwt_required
    def get(self):
        '''Get the active calendar configuration'''
        identity = auth_services.get_identity()
        link = calendar_service.generate_cal_link_for_user(identity)
        return {"link" : link}


@api.route("/<token>/calendar.ics")
class UserCalendarExport(Resource):
    @api.doc("download_user_calendar")
    def get(self, token):
        result = calendar_service.get_ics(token)

        return Response(
            result,
            mimetype="text/calendar",
            headers={"Content-disposition":
                         "attachment; filename=calendar.ics"})
