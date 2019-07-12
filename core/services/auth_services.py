import core.database.users_db as users_db
import core.services.emailer_service as emailer_service
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
import uuid
import os
import datetime


def check_login(user_email, password):
    user = users_db.get_user_by_email(user_email)
    if user is None or user["hashed_password"] is None:
        return False
    else:
        if sha256.verify(password, user["hashed_password"]):
            token = create_access_token(identity=user["pk"])
            return token
        return False


def set_password(user_email, password):
    user = users_db.get_user_by_email(user_email)
    user["hashed_password"] = sha256.hash(password)
    if users_db.update_user(user):
        return
    else:
        raise Exception("Failed to create user")


@jwt_required
def get_identity():
    return get_jwt_identity()


def request_password_reset(user_email):
    user = users_db.get_user_by_email(user_email)
    if user is None:
        return False
    reset_token = uuid.uuid4().hex
    expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
    token_result = users_db.set_password_reset_token(user_email, reset_token,expiration)
    if token_result:
        body = 'Hello,<br /><br />Please click on <a href="%s">this link</a> ' \
               'to reset your Otter Pond password. The link will expire in' \
               ' one hour.<br /><br />Thank you,<br /><br />The Otter Pond Team'
        stage = os.environ.get("stage")
        if not stage:
            stage = "dev"
        link = "https://%s.theotterpond.com/auth/resetPassword?token=%s" % (stage, reset_token)
        body = body % link
        result = emailer_service.send_html_body("Password Reset", body, [user_email])
        return result
    return False


def reset_password(user_email, token, password):
    user_token = users_db.get_user_token(user_email)
    if user_token is None:
        return False

    now = datetime.datetime.now()
    if user_token["expiration"] < now:
        return False

    if user_token["token"] != token:
        return False

    set_password(user_email, password)

    users_db.delete_item(user_email, "resetToken")
    return True