from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required, get_jwt_identity

from blocklist import BLOCKLIST
from db import db
from sqlalchemy.exc import SQLAlchemyError

import os, requests
from sqlalchemy import or_

from models import UserModel
from marshmallow_schema.schemas import UserSchema, RegisterUserSchema

blueprint = Blueprint("users",__name__,description="Operation on users")

def send_simple_message(to, object, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    api = os.getenv("MAILGUN_API_KEY")
    
    return requests.post(
  		f"https://api.mailgun.net/v3/{domain}/messages",
  		auth=("api", api),
  		data={"from": f"Mailgun Sandbox <postmaster@{domain}>",
			"to": [to],
  			"subject": object,
  			"text": body
        }
    )

@blueprint.route("/user/<int:user_id>")
class User(MethodView):

    @jwt_required()
    @blueprint.response(201, UserSchema)
    def get(get, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required()
    def delete(get, user_id):
        user = UserModel.query.get_or_404(user_id)
        
        try:
            db.session.delete(user)
            db.session.commit()

            return {"message":"User deleted sucsessfully."}
        except SQLAlchemyError:
            abort(500, message = "Error while deleting user")

@blueprint.route("/register")
class UserRegister(MethodView):

    @blueprint.arguments(RegisterUserSchema)
    @blueprint.response(201, RegisterUserSchema)
    def post(self, user_data):
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"])
            ).first():
            abort(409, message="Username or email already exist in the system.Try another one.")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]))
        
        try:
            db.session.add(user)
            db.session.commit()
            
            send_simple_message(
                to=user.email,
                object="User registration",
                body=f"You have succesfully registered {user.username} to our database API."
            )

            return user        
        except SQLAlchemyError:
            abort(500, message = "Error while creating user")

@blueprint.route("/login")
class UserLogin(MethodView):

    @blueprint.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):

            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            return {"access token" : access_token, "refresh token" : refresh_token}
        abort(401, message = "Login credentials are ivalid, retry with correct ones.")
        
 
@blueprint.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message" : "Successfully logged out."}
    
@blueprint.route("/refresh")
class UserRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id,fresh=False)
        
        return {"access token" : new_token}
