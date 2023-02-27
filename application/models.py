from .database import db


class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String, primary_key=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String)


class Decks(db.Model):
    __tablename__ = "decks"
    deck_id = db.Column(db.String, primary_key=True)
    deck_name = db.Column(db.String)
    description = db.Column(db.String)
    cards = db.relationship("Cards", backref="deck")


class User_table(db.Model):
    __tablename__ = "user_table"
    username = db.Column(db.String, db.ForeignKey("user.username"), primary_key=True, nullable=False)
    deck_id = db.Column(db.String, db.ForeignKey("decks.deck_id"), primary_key=True, nullable=False)
    score = db.Column(db.Integer, default=0)


class Cards(db.Model):
    __tablename__ = "cards"
    deck_id = db.Column(db.String, db.ForeignKey("decks.deck_id"), nullable=False)
    card_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    front = db.Column(db.String, nullable=False, unique=True)
    back = db.Column(db.String, nullable=False)
    hard = db.Column(db.Integer, default=0)
    easy = db.Column(db.Integer, default=0)
    good = db.Column(db.Integer, default=0)
