from flask import request, Response
from flask_restplus import Namespace, Resource, fields
from api.models.payment_model import enroll_model, verify_model, charge_model, execute_model
from flask_jwt_extended import jwt_required
import core.services.payment_service as payment_service
import json


api = Namespace('payment', description='Payment related operations')

api.models[enroll_model.name] = enroll_model
api.models[verify_model.name] = verify_model
api.models[charge_model.name] = charge_model
api.models[execute_model.name] = execute_model


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
    @api.doc("Used to directly charge a user, i.e. submitting this will create the report entry and send it to Stripe")
    @api.expect(charge_model)
    @jwt_required
    def post(self):
        '''Charge a user'''
        body = request.json
        print("Received Charge Request: ", body)
        result = payment_service.create_charge(body["amount"])
        print("Result of Charge: ", result)
        return {"error": result}


@api.route("/prepareCharge")
class PreparePaymentCharge(Resource):
    @api.doc("Used to indicate that a user is ready to be charged. Creates a report entry and gives it the status of PENDING APPROVAL")
    @api.expect(charge_model)
    @jwt_required
    def post(self):
        '''Prepare a charge '''
        body = request.json
        result = payment_service.prepare_charge(body["amount"])
        return {"error": "Success"}


@api.route("/executeCharge")
class ExecutePaymentCharge(Resource):
    @api.doc("Used to execute a charge that has previously been prepared")
    @api.expect(execute_model)
    @jwt_required
    def post(self):
        '''Execute a charge'''
        body = request.json
        result = payment_service.execute_charge(body["report_entry_id"])
        return {"error": "Success"}


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