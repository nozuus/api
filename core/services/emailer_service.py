import core.database.email_list_db as email_list_db
import core.database.users_db as users_db
import boto3
import email


def process_received_email(mail):
    message_id = mail["messageId"]
    to_emails = mail["destination"]
    destinations = []
    total_emails = []
    for to_email in to_emails:
        email_list = get_list_by_address(to_email)
        if email_list is not None:
            user_emails = get_emails_for_list(email_list["list_id"])
            for user_email in user_emails:
                if user_email in total_emails:
                    user_emails.remove(user_email)
                else:
                    total_emails.append(user_email)
            destinations.append((email_list["subject_prefix"], user_emails))

    print("Destinations: ", destinations)

    email_contents = read_email_from_s3(message_id)
    msg = email.message_from_bytes(email_contents)

    msg_from = msg["From"]
    from_name, from_email = split_from(msg_from)
    del msg['Return-Path']
    del msg['From']
    del msg['Reply-To']
    safe_from = '%s <mailer@email.theotterpond.com>' % (from_name)
    user_from = "%s <%s>" % (from_name, from_email)
    msg["Reply-To"] = user_from
    msg["From"] = safe_from
    msg["Return-Path"] = "mailer@email.theotterpond.com"
    msg["Source"] = "mailer@email.theotterpond.com"

    original_subject = msg["Subject"]
    for subject_prefix, user_emails in destinations:
        new_subject = "[" + subject_prefix + "] " + original_subject
        del msg["Subject"]
        msg["Subject"] = new_subject
        send_email(msg, user_emails)


def split_from(msg_from):
    msg_from_split = msg_from.split("<")
    msg_from_name = msg_from_split[0];
    msg_from_email = msg_from_split[1].split(">")[0]
    return msg_from_name, msg_from_email


def get_list_by_address(to_email):
    split = to_email.split("@")
    prefix = split[0]
    domain = split[1]
    # Get Email List
    email_list = email_list_db.get_email_list(prefix, domain)
    return email_list


def get_emails_for_list(list_id):
    # Get Subscriptions
    users_on_list = email_list_db.get_users_on_list(list_id)
    user_emails = []
    for user_on_list in users_on_list:
        user_emails.append(user_on_list["user_primary_email_address"])

    return user_emails


def send_email(msg, email_addresses):
    email_client = boto3.client('ses')
    email_client.send_raw_email(
        Destinations=email_addresses,
        RawMessage={
            'Data': msg.as_string()
        },
    )


def read_email_from_s3(message_id):
    s3 = boto3.resource("s3")
    key = "received/" + message_id
    obj = s3.Object("otter-pond-emails", key)
    file_contents = obj.get()['Body'].read()
    return file_contents
