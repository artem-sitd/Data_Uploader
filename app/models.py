from .db import db


class Dataset(db.Model):
    __tablename__ = "datasets" # будет использовать это имя таблицы в БД
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

    # связь OtM, с обратной связью
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

    # колонка на Dataset, не сможет записать несуществующий datasets.id'
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))


class DatasetStats(db.Model):
    __tablename__ = "dataset_stats"
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), unique=True)
    mean = db.Column(db.Float)
    max = db.Column(db.Float)
    std = db.Column(db.Float)
    peaks = db.Column(db.Integer)
    plot_html = db.Column(db.Text)

    # связь 1к1 uselist=False делает связь одиночной, а не списком (в отличие от .datapoints)
    dataset = db.relationship("Dataset", backref=db.backref("stats", uselist=False))
