import stripe
import os
import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
import core.database.users_db as users_db
import core.database.db as base_db
import core.services.config_service as config_service
import core.services.reporting_service as reporting_service
import json
import logging

import core.services.emailer_service as emailer

stripe.api_key = os.environ.get("STRIPE_KEY")

logger = logging.getLogger()


@jwt_required
def enroll_stripe_token(token):
    user_email = get_jwt_identity()
    user = users_db.get_user_by_email(user_email)
    name = user["last_name"] + ", " + user["first_name"]
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

    customer = stripe.Customer.create(source=token, name=name,
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
    try:
        user_email = get_jwt_identity()
        payment_record = base_db.get_item(user_email, "payment")
        amount = int(float(amount) * 100)
        if not payment_record:
            raise Exception("Error fetching payment record")

        if payment_record["status"] != "Verified":
            return "Account is not verified"

        try:
            logger.warning("Creating charge")
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                customer=payment_record["customer_id"]
            )
            logger.warning("Charge Created:")
            logger.warning(json.dumps(charge))
        except stripe.error.InvalidRequestError:
            return "Invalid Amount"

        if charge["status"] == "pending":
            amount_post_fees = int(.992 * amount) / 100
            amount_post_fees = -(amount_post_fees if (amount / 100) - amount_post_fees < 5 else (amount / 100) - 5)

            logger.warning("--- CHARGE CREATED ---")
            logger.warning(json.dumps(charge))

            report_entry = {
                "description": "Payment " + charge["id"],
                "value": amount_post_fees,
                "status": "PENDING",
                "report_id": get_active_finances_report(),
                "entered_by_email": user_email,
                "user_email": user_email,
                "timestamp": datetime.datetime.now()
            }

            logger.warning("Creating report entry")
            logger.warning(report_entry)

            entry_id = reporting_service.create_report_entry(report_entry["report_id"], report_entry, bypass_permissions=True)

            logger.warning("Report entry created: %s. Notifying admin" % entry_id)

            notify_financial_manager(charge["id"], "PENDING")

            logger.warning("Admin notified")
            return "Success"
    except Exception as e:
        logger.error("ERROR CREATING CHARGE")
        logger.error(e)
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


    print("--- PAYMENT WEBHOOK ---")
    print(json.dumps(event))
    if event.type == "charge.succeeded":
        print("Payment Succeeded")
        payment_id = event.data.object.id
        print("Payment ID: " + payment_id)
        update_payment_status(payment_id, "CLEARED")
        print("Payment status updated to CLEARED")
        print("Sending email to financial manager")
        notify_financial_manager(payment_id, "CLEARED")
        print("Notified financial manager")
    elif event.type == "charge.failed":
        failure_reason = event.data.object.failure_message
        print("Failed: " + failure_reason)

        failure_reason += " A $4 fee has been applied to this customers account"
        payment_id = event.data.object.id
        print("Payment ID: " + payment_id)
        update_payment_status(payment_id, "FAILED")
        print("Payment status updated to FAILED")
        failed_ach(payment_id)
        print("Created entries for failed ACH transaction")
        notify_financial_manager(payment_id, "FAILED", failure_reason)
        print("Notified financial manager")
    elif event.type == "customer.source.updated":
        print("Updated Bank Info")
    else:
        print("Received other webhook: ")
        print(json.dumps(event))


def update_payment_status(payment_id, new_status):
    found_entry = get_payment(payment_id)

    found_entry["status"] = new_status
    base_db.put_item_no_check(found_entry)


def get_payment(payment_id):
    report_id = get_active_finances_report()
    entries = reporting_service.get_report_entries(report_id, True)
    entry_description = "Payment " + payment_id
    for entry in entries:
        if entry["description"] == entry_description:
            return entry
    return None


def failed_ach(payment_id):
    failed_payment = get_payment(payment_id)
    report_entry = {
        "description": "Failed Payment " + payment_id,
        "value": -float(failed_payment["value"]),
        "report_id": get_active_finances_report(),
        "entered_by_email": failed_payment["user_email"],
        "user_email": failed_payment["user_email"],
        "timestamp": datetime.datetime.now()
    }

    reporting_service.create_report_entry(report_entry["report_id"],
                                          report_entry, bypass_permissions=True)

    fees_entry = {
        "description": "Fee for Failed Payment " + payment_id,
        "value": 4.00,
        "report_id": get_active_finances_report(),
        "entered_by_email": failed_payment["user_email"],
        "user_email": failed_payment["user_email"],
        "timestamp": datetime.datetime.now()
    }

    reporting_service.create_report_entry(report_entry["report_id"],
                                          fees_entry, bypass_permissions=True)


def notify_financial_manager(payment_id, status, reason = None):
    email = "Dear Financial Manager,\n\nA payment for the following user has been updated.\n\n"

    payment = get_payment(payment_id)
    user = users_db.get_user_by_email(payment["user_email"])
    email += "User: " + user["last_name"] + ", " +  user["first_name"]
    email += "\nAmount: " + str(abs(payment["value"]))
    email += "\nStatus: " + status

    if reason is not None:
        email += "\nStatus Reason: " + reason

    email += "\n\nit'get dat money'b\n\nOtter Pond"
    subject = "Otter Pond Payment: " + status
    to_emails = [get_active_finance_email()]

    print("Sending email:")
    print(json.dumps(email))
    emailer.send_plain_email(subject, email, to_emails)


def get_active_finances_report():
    setting = config_service.get_setting_by_identifer("finance_report")
    if setting is None:
        raise Exception("No Active Finance Report")

    return setting["value"]


def get_active_finance_email():
    setting = config_service.get_setting_by_identifer("finance_email")
    if setting is None:
        raise Exception("No Active Finance Email")

    return setting["value"]