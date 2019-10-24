import stripe
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
import core.database.users_db as users_db
import core.database.db as base_db

stripe.api_key = os.environ.get("STRIPE_KEY")


@jwt_required
def enroll_stripe_token(token):
    user_email = get_jwt_identity()
    user = users_db.get_user_by_email(user_email)
    description = user["last_name"] + ", " + user["first_name"]
    customer = stripe.Customer.create(source=token, description=description,
                                      email=user_email)

    bank_account_id = customer["sources"]["data"][0]["id"]
    payment_record = {
        "pk": user_email,
        "sk": "payment",
        "customer_id": customer["id"],
        "bank_account_id": bank_account_id,
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

    bank_account = stripe.Customer.retrieve_source(payment_record["customer_id"], payment_record["bank_account_id"])

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
