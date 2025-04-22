from .db import db


class Dataset(db.Model):
    __tablename__ = "datasets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    datapoints = db.relationship('DataPoint', backref='dataset', lazy=True)


class DataPoint(db.Model):
    __tablename__ = "datapoints"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    emg1 = db.Column(db.Integer)
    emg2 = db.Column(db.Integer)
    emg3 = db.Column(db.Integer)
    emg4 = db.Column(db.Integer)
    angle = db.Column(db.Integer)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
