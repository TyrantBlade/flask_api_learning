from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required, get_jwt_identity

from blocklist import BLOCKLIST
from db import db
from sqlalchemy.exc import SQLAlchemyError

from models import UserModel
from schemas import UserSchema

blueprint = Blueprint("users",__name__,description="Operation on users")

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

    @blueprint.arguments(UserSchema)
    @blueprint.response(201, UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="Username already exist in the system.Try another one.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]))
        
        try:
            db.session.add(user)
            db.session.commit()
            
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
