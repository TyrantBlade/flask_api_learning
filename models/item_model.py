from models.time_model import TimeModel, db

class ItemModel(TimeModel):
    __tablename__= "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String())
    price = db.Column(db.Float(precision=2), nullable=False, unique=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False, unique=False)

    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items", secondary="tags_items")