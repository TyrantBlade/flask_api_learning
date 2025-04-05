from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    description = fields.Str(required=True)


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    
class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Str()

class ItemSchema(PlainItemSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema, dump_only=True)


class StoreSchema(PlainStoreSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema, dump_only=True))
    tags = fields.List(fields.Nested(PlainTagSchema, dump_only=True))


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema, dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema, dump_only=True))

class TagsAndItemsSchema():
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)
    message = fields.Str()