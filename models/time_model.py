from sqlalchemy.event import listens_for
from datetime import datetime
from db import db

class TimeModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@listens_for(TimeModel, 'before_update', named=True)
def update_timestamps(mapper, connection, target):
    target.updated_at = datetime.utcnow()