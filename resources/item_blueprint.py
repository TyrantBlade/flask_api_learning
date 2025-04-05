from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import db
from flask_jwt_extended import get_jwt, jwt_required
from sqlalchemy.exc import SQLAlchemyError

from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blueprint = Blueprint("items",__name__,description = "Operations on items")

@blueprint.route("/item/<int:item_id>")
class Items(MethodView):

    @blueprint.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item
    
    @jwt_required()
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)

        jwt = get_jwt()

        if not jwt.get("is_admin"):
            abort(401, message = "Admin privileges required.")
        
        db.session.delete(item)
        db.session.commit()
        return {"Message" : "Item deleted successfully."}

    @jwt_required()
    @blueprint.arguments(ItemUpdateSchema)
    @blueprint.response(201, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()
        
        return item

@blueprint.route("/item")
class ItemList(MethodView):

    @blueprint.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required()
    @blueprint.arguments(ItemSchema)
    @blueprint.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message = "Error item not inserted due to error.")

        return item,201