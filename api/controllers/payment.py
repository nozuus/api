from flask import request, Response
from flask_restplus import Namespace, Resource, fields
from api.models.payment_model import enroll_model, verify_model, charge_model
from flask_jwt_extended import jwt_required
import core.services.payment_service as payment_service
import json


api = Namespace('payment', description='Payment related operations')

api.models[enroll_model.name] = enroll_model
api.models[verify_model.name] = verify_model
api.models[charge_model.name] = charge_model


@api.route("/enroll")
class PaymentEnroll(Resource):
    @api.doc("enroll_payment")
    @api.expect(enroll_model)
    @jwt_required
    def post(self):
        '''Enroll current user in Stripe payment.'''
        body = request.json
        token = body["stripeToken"]
        payment_service.enroll_stripe_token(token)
        return {"error": "Success"}


@api.route("/verify")
class PaymentVerify(Resource):
    @api.doc("verify_payment")
    @api.expect(verify_model)
    @jwt_required
    def post(self):
        '''Verify a user's payment method'''
        body = request.json
        amounts = [body["firstDeposit"], body["secondDeposit"]]
        result = payment_service.verify_account(amounts)
        if result:
            return {"error": "Success"}
        else:
            return {"error": "Invalid Amounts"}


@api.route("/charge")
class PaymentCharge(Resource):
    @api.doc("charge_user")
    @api.expect(charge_model)
    @jwt_required
    def post(self):
        '''Charge a user'''
        body = request.json
        print("Received Charge Request: ", body)
        result = payment_service.create_charge(body["amount"])
        print("Result of Charge: ", result)
        return {"error": result}


@api.route("/webhook")
class PaymentWebhook(Resource):
    @api.doc("webhook")
    def post(self):
        '''Webhook for stripe integration'''
        body = request.json
        payment_service.process_webhook(body)
        return {"error": "Success"}


@api.route("/account")
class CheckAccountStatus(Resource):
    @api.doc("check_account_status")
    @jwt_required
    def get(self):
        '''Check if the current user has a setup and verified account'''
        result = payment_service.get_account_status()
        return result

    @api.doc("delete_bank_account")
    @jwt_required
    def delete(self):
        '''Removes a users bank accouunt'''
        result = payment_service.delete_account()
        return {"error": "Success"}