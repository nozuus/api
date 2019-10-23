import json
import core.database.email_list_db as email_list_db
import core.database.users_db as users_db
import boto3
import email
import json
import os
import datetime


def email_received(event, context):
    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    if message["notificationType"] == "Received":
        mail = message["mail"]
        process_received_email(mail)

    else:
        print("Message not received. Terminating")


def process_received_email(mail):
    try:
        print("Mail object: ")
        print(mail)
        message_id = mail["messageId"]
        print("Message ID: " + message_id)

        if email_list_db.check_message_id(message_id):
            print("Message ID exists in cache. Terminating.")
            send_admin_email("Message in cache")
            return
        else:
            email_list_db.store_message_id(message_id, str(datetime.datetime.now()))

        to_emails = mail["destination"]
        print("To emails: ", to_emails)
        metadata_from = mail["source"]
        #Putting a hold on this for now
        find_embedded_to_address(mail["headers"], to_emails)
        print("Metadata from: ", metadata_from)
        destinations = []
        total_emails = []
        allow_external = True
        for to_email in to_emails:
            to_email = to_email.lower()
            email_list = email_list_db.get_email_list_by_address(to_email)
            if email_list is not None:
                print("Email list found for recipient: " + to_email)
                if not email_list["allow_external"]:
                    allow_external = False
                user_emails = get_emails_for_list(to_email)
                users_to_send_to = []
                for user_email in user_emails:
                    # Don't add the user if they're already being sent it, or if
                    # they were the sender or are already a recipient
                    if (user_email not in total_emails
                            #and user_email != metadata_from
                            and user_email not in to_emails):
                        total_emails.append(user_email)
                        users_to_send_to.append(user_email)
                print("Found %d users for list." % len(users_to_send_to))
                if len(users_to_send_to) > 0:
                    destinations.append((email_list["subject_prefix"],
                                         users_to_send_to))
            else:
                print("Email list not found for recipient: " + to_email)

        print("Destinations: ", destinations)

        print("Reading email contents from S3")
        email_contents = read_email_from_s3(message_id)
        print("Finished reading email contents from S3")
        msg = email.message_from_bytes(email_contents)

        if len(destinations) == 0:
            print("Invalid destinations. Sending bounce")
            #send_admin_email("Invalid Destination")
            #send_invalid_destination_email(metadata_from, to_emails, msg["Subject"])
            return

        if not allow_external:
            if not check_valid_from_email(metadata_from):
                print("Invalid from email. Sending bounce")
                send_admin_email("Invalid from email")
                #send_invalid_from_email(metadata_from, to_emails, msg["Subject"])
                return

        msg_from = msg["From"]
        from_name, from_email = split_from(msg_from)
        del msg['Return-Path']
        del msg['From']
        del msg['Reply-To']
        del msg['Source']
        safe_from = '%s <mailer@email.theotterpond.com>' % (from_name)
        user_from = "%s <%s>" % (from_name, from_email)
        msg["Reply-To"] = user_from
        msg["From"] = safe_from
        msg["Return-Path"] = "mailer@email.theotterpond.com"
        msg["Source"] = "mailer@email.theotterpond.com"

        original_subject = msg["Subject"]
        for subject_prefix, user_emails in destinations:
            if subject_prefix is not None and subject_prefix not in original_subject:
                new_subject = "[" + subject_prefix + "] " + original_subject
                del msg["Subject"]
                msg["Subject"] = new_subject
            if subject_prefix is not None:
                print("Sending to users on list with prefix: " + subject_prefix)
            else:
                print("Sending to user without prefix")
            if len(user_emails) >= 50:
                chunked_emails = chunks(user_emails, 50)
                for user_chunks in chunked_emails:
                    send_email(msg, user_chunks)
            else:
                send_email(msg, user_emails)
        print("Succeeded processing email")
    except Exception as e:
        print("Exception. Printing object and serialized object: ")
        print(e)
        send_admin_email("Exception")
    print("Finished email processing execution")


def split_from(msg_from):
    msg_from_split = msg_from.split("<")
    msg_from_name = msg_from_split[0];
    msg_from_email = msg_from_split[1].split(">")[0]
    return msg_from_name, msg_from_email


def get_emails_for_list(address):
    # Get Subscriptions
    users_on_list = email_list_db.get_users_on_list(address)
    user_emails = []
    for user_on_list in users_on_list:
        user_emails.append(user_on_list["pk"])

    return user_emails


def send_email(msg, email_addresses):
    print("Sending email to users: " + ", ".join(email_addresses))
    email_client = boto3.client('ses')
    response = email_client.send_raw_email(
        Destinations=email_addresses,
        RawMessage={
            'Data': msg.as_string()
        },
    )
    print("Send Email Response: " + json.dumps(response))


def read_email_from_s3(message_id):
    s3 = boto3.resource("s3")
    key = "received/" + message_id
    obj = s3.Object("otter-pond-emails", key)
    file_contents = obj.get()['Body'].read()
    return file_contents


def send_invalid_destination_email(from_email, to_emails, subject):
    message = {
        'Subject': {
            "Data": "Unable to send: %s" % subject,
        },
        "Body": {
            "Text": {
                "Data": "Dear %s, \n\n\nYour email sent to %s did not contain "
                        "a valid destination for this domain. Please "
                        "check your recipients and try again. If you believe "
                        "this is an error, please send an email to "
                        "dbecker.fl@gmail.com.\n\nThank you,\n\nDaniel Becker"
                        % (from_email, ",".join(to_emails))
            }
        }
    }

    print(message)
    email_client = boto3.client('ses')
    email_client.send_email(Source= "Otter Pond Emailer <noreply@email.theotterpond.com>",
                            Destination={"ToAddresses": [from_email]},
                            Message=message)


def send_invalid_from_email(from_email, to_emails, subject):
    message = {
        'Subject': {
            "Data": "Unable to send: %s" % subject,
        },
        "Body": {
            "Text": {
                "Data": "Dear %s, \n\n\nYou do not have permissions to send an "
                        "email to %s. If you have an account for Otter Pond, "
                        "this error could be because this email is not listed "
                        "under your account. If you believe this is an error, "
                        "please send an email to dbecker.fl@gmail.com.\n\n"
                        "Thank you,\n\nDaniel Becker"
                        % (from_email, ",".join(to_emails))
            }
        }
    }

    print(message)
    email_client = boto3.client('ses')
    email_client.send_email(Source= "Otter Pond Emailer <noreply@email.theotterpond.com>",
                            Destination={"ToAddresses": [from_email]},
                            Message=message)


def check_valid_from_email(from_email):
    check_user = users_db.get_user_by_email(from_email)
    if check_user:
        return True
    # now the rough one. Grab all users, check their other emails
    all_users = users_db.get_all_users()
    for user in all_users:
        if from_email in user["other_emails"]:
            return True
    return False


def find_embedded_to_address(headers, to_emails):
    print(headers)
    for header in headers:
        if header["name"] == "Received":
            if "for " in header["value"]:
                print("Found for address in received header. Parsing value")
                value = header["value"]
                address = header["value"][(value.index("for ") + 4):value.index(";")]
                print("Address: " + address)
                if address not in to_emails:
                    send_admin_email("Invalid embedded to address")
                return


def send_admin_email(reason=""):
    admin_email = os.environ['admin_email']
    if admin_email is None or admin_email == "":
        print("Admin email not found. Terminating")
        return
    message = {
        'Subject': {
            "Data": "Admin Email" if reason == "" else  "Admin Email: " + reason,
        },
        "Body": {
            "Text": {
                "Data": "Please check the logs from %s for an item needing "
                        "attention." % (str(datetime.datetime.now()))

            }
        }
    }

    print(message)
    email_client = boto3.client('ses')
    email_client.send_email(Source= "Otter Pond Emailer <noreply@email.theotterpond.com>",
                            Destination={"ToAddresses": [admin_email]},
                            Message=message)

    print("Send email to admin")

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
