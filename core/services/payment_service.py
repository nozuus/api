import stripe
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
import core.database.users_db as users_db
import core.database.db as base_db
import json

stripe.api_key = os.environ.get("STRIPE_KEY")


@jwt_required
def enroll_stripe_token(token):
    user_email = get_jwt_identity()
    user = users_db.get_user_by_email(user_email)
    description = user["last_name"] + ", " + user["first_name"]
    payment_record = base_db.get_item(user_email, "payment")

    if payment_record is not None:
        customer = stripe.Customer.retrieve(payment_record["customer_id"])

        if "deleted" not in customer or not customer["deleted"]:

            for source in customer.sources:
                stripe.Customer.delete_source(payment_record["customer_id"], source["id"])

            stripe.Customer.create_source(payment_record["customer_id"], source=token)

            payment_record["status"] = "Pending Verification"
            base_db.put_item_no_check(payment_record)
            return True

    customer = stripe.Customer.create(source=token, description=description,
                                      email=user_email)

    payment_record = {
        "pk": user_email,
        "sk": "payment",
        "customer_id": customer["id"],
        "status": "Pending Verification"
    }
    return base_db.put_item_no_check(payment_record)


@jwt_required
def verify_account(amounts):
    user_email = get_jwt_identity()
    payment_record = base_db.get_item(user_email, "payment")
    if not payment_record:
        raise Exception("Error fetching payment record")

    if payment_record["status"] == "Verified":
        raise Exception("Account Already Verified")

    customer = stripe.Customer.retrieve(payment_record["customer_id"])
    bank_account_id = customer["sources"]["data"][0]["id"]

    bank_account = stripe.Customer.retrieve_source(payment_record["customer_id"], bank_account_id)

    try:
        bank_account.verify(amounts=amounts)
        payment_record["status"] = "Verified"
        base_db.put_item_no_check(payment_record)
        return True
    except stripe.error.CardError:
        return False


@jwt_required
def create_charge(amount):
    user_email = get_jwt_identity()
    payment_record = base_db.get_item(user_email, "payment")
    amount = int(amount * 100)
    if not payment_record:
        raise Exception("Error fetching payment record")

    if payment_record["status"] != "Verified":
        return "Account is not verified"

    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            customer=payment_record["customer_id"]
        )
    except stripe.error.InvalidRequestError:
        return "Invalid Amount"

    if charge["status"] == "pending":
        return "Success"
    return charge


def get_account_status():
    user_email = get_jwt_identity()
    payment_record = base_db.get_item(user_email, "payment")
    if not payment_record:
        return {"accountStatus": "None"}

    customer = stripe.Customer.retrieve(payment_record["customer_id"])
    if "sources" not in customer or len(customer.sources) == 0:
        return {"accountStatus": "None"}
    account = customer.sources.data[0]
    account_name = account.bank_name + " " + account.last4
    account_status = account.status
    return {
        "accountName": account_name,
        "accountStatus": account_status
    }


def delete_account():
    user_email = get_jwt_identity()
    payment_record = base_db.get_item(user_email, "payment")
    if not payment_record:
        raise Exception("Error fetching payment record")

    customer = stripe.Customer.retrieve(payment_record["customer_id"])

    if "deleted" not in customer or not customer["deleted"]:

        for source in customer.sources:
            stripe.Customer.delete_source(payment_record["customer_id"],
                                          source["id"])
        return True
    raise Exception("Invalid customer")


def process_webhook(payload):
    try:
        event = stripe.Event.construct_from(
            payload, stripe.api_key
        )
    except ValueError as e:
        raise Exception("Invalid payload")

    if event.type == "charge.succeeded":
        print("Succeeded")
    elif event.type == "charge.failed":
        failure_reason = event.data.object.failure_message
        print("Failed: " + failure_reason)
    elif event.type == "customer.source.updated":
        print("Updated Bank Info")
    else:
        raise Exception("Unknown event type")
