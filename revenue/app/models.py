from revenue.app import db


class Entry(db.Model):
    __tablename__ = 'entries'

    """
    Sample Entry
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, nullable=False)
