from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from db import db
from sqlalchemy.exc import SQLAlchemyError

from models import TagModel, StoreModel, ItemModel
from marshmallow_schema.schemas import TagSchema, TagsAndItemsSchema

blueprint = Blueprint("tags",__name__,description="Operation on tags")

@blueprint.route("/store/<int:store_id>/tags")
class TagInStore(MethodView):

    @blueprint.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()
    
    @jwt_required()
    @blueprint.arguments(TagSchema)
    @blueprint.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=e)

        return tag
    


@blueprint.route("/tag/<int:tag_id>")
class Tag(MethodView):

    @blueprint.response(201, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
            
        return tag
    
    @jwt_required()    
    @blueprint.response(201, TagSchema)
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:

            try:
                db.session.delete(tag)
                db.session.commit()
                return {"message" : "Tag was deleted"}
            except SQLAlchemyError:
                abort(500, message = "Tag was not deleted")

        return tag

    

@blueprint.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItems(MethodView):

    @jwt_required()
    @blueprint.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message = "An error appear when adding a tag")

        return tag
    
    @jwt_required()
    @blueprint.response(201, TagsAndItemsSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message = "An error appear when removing a tag")

        return tag