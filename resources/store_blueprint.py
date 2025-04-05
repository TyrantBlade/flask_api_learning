from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import StoreSchema
from models import StoreModel

blueprint = Blueprint("stores",__name__,description = "Operations on stores")

@blueprint.route("/store/<int:store_id>")
class Stores(MethodView):

    @blueprint.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        
        db.session.delete(store)
        db.session.commit()
        return {"Message" : "Store deleted successfully."}



@blueprint.route("/store")
class StoreList(MethodView):

    @blueprint.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @blueprint.arguments(StoreSchema)
    @blueprint.response(201, StoreSchema)
    def post(self, store_data):

        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message = "A store with that name already exist.")
        except SQLAlchemyError:
            abort(500, message = "Error store not created due to error.")


        return store,201