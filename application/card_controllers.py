from flask import Flask, request, render_template, redirect, url_for,g
from flask import current_app as app
from application.models import *
from flask import session
from flask_restful import Resource, fields, marshal_with, reqparse
from application.validations import *

#import requests

deck_output = {
    "deck_id": fields.String,
    "deck_name": fields.String,
    "description": fields.String
}

card_output = {
    "front": fields.String,
    "back": fields.String,
    "card_id": fields.Integer,
    "deck_id": fields.String
}

error_dict = {
    "D1e": ("DECK01", "Deck id should not have spaces and in caps"),
    "D2e": ("DECK02", "deck id and/or deck name can not be empty"),
    "D3e": ("DECK03", "deck id already exists"),
    "C1e": ("CARD01", "Card question already exists"),
    "C2e": ("CARD02", "Card question and/or answer can not be empty"),
    "C3e": ("CARD03", "You need to add card first"),
    "S1e": ("SCORE01", "You need to select an option"),
    "R1e": ("RE01", "You need to select an option for Review")
}

# =================================== DECK API =================================== #

class DeckAPI(Resource):

    @marshal_with(deck_output)
    def get(self, deck_id):
        deck = db.session.query(Decks).filter(Decks.deck_id == deck_id).first()
        if deck:
            return deck
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(deck_output)
    def put(self, deck_id):
        try:
            deck_name = request.form['name']
        except KeyError:
            deck_name = None
        try:
            description = request.form['description']
        except KeyError:
            description = None
        deck = db.session.query(Decks).filter(Decks.deck_id == deck_id).first()
        if deck is None:
            raise NotFoundError(404)
        elif deck_name == ' ':
            raise BusinessValidationError(400, error_code=error_dict['D2e'][0], error_msg=error_dict['D2e'][1])
        if deck_name:
            deck.deck_name = deck_name
        if description:
            deck.description = description

        # db.session.add(deck)
        db.session.commit()
        return deck

    def delete(self, deck_id):
        ud = None
        deck = db.session.query(User_table).filter(User_table.username == session['username']).all()
        for i in deck:
            if i.deck_id == deck_id:
                ud = i
        if ud:
            db.session.delete(ud)
            db.session.commit()
        else:
            raise NotFoundError(404)
        return

    def post(self):
        try:
            deck_id = request.form['deck_id']
            deck_name = request.form['deck_name']
        except KeyError:
            raise BusinessValidationError(400, error_code=error_dict['D2e'][0], error_msg=error_dict['D2e'][1])
        try:
            description = request.form['description']
        except KeyError:
            description = None

        decks = db.session.query(Decks).filter(Decks.deck_id == deck_id).first()
        if decks:
            raise BusinessValidationError(400, error_code=error_dict['D3e'][0], error_msg=error_dict['D3e'][1])
        for i in deck_id:
            if i == ' ':
                raise BusinessValidationError(400,  error_code=error_dict['D1e'][0], error_msg=error_dict['D1e'][1])
        new_deck = Decks(deck_id=deck_id, deck_name=deck_name, description=description)
        new_relation = User_table(username=session['username'], deck_id=deck_id, score=0)
        db.session.add(new_deck)
        db.session.add(new_relation)
        db.session.commit()
        return new_deck.deck_id

# =================================== CARD API =================================== #


class CardAPI(Resource):
    @marshal_with(card_output)
    def get(self, deck_id, card_id):
        try: 
            card = db.session.query(Cards).filter(Cards.card_id == card_id).first()
        except:
            raise BusinessValidationError(400, error_code=error_dict['C3e'][0], error_msg=error_dict['C3e'][1])
        finally:
            if card.deck_id == deck_id:
                if card:
                    return card
                raise NotFoundError(status_code=404)
            raise NotFoundError(status_code=404)

    @marshal_with(card_output)
    def put(self, deck_id, card_id):
        try:
            front = request.form['front']
        except KeyError:
            front = None
        try:
            back = request.form['back']
        except KeyError:
            back = None
        card = db.session.query(Cards).filter(Cards.card_id == card_id).first()
        if card is None:
            raise NotFoundError(404)
        elif card.deck_id != deck_id:
            raise NotFoundError(404)
        elif front == ' ':
            raise BusinessValidationError(400, error_code=error_dict['C2e'][0], error_msg=error_dict['C2e'][1])
        elif back == ' ':
            raise BusinessValidationError(400, error_code=error_dict['C3e'][0], error_msg=error_dict['C3e'][1])
        dup_front = db.session.query(Cards).filter(Cards.front == front).first()
        p = None
        if dup_front:
            if dup_front.card_id == card_id:
                    p = dup_front
        if p:
            raise BusinessValidationError(400, error_code=error_dict['C1e'][0], error_msg=error_dict['C1e'][1])
        if front:
            card.front = front
        if back:
            card.back = back
        db.session.commit()
        return card

    def delete(self, deck_id, card_id):
        card = db.session.query(Cards).filter(Cards.card_id == card_id).first()
        if card is None:
            raise NotFoundError(404)
        elif card.deck_id !=deck_id:
            raise NotFoundError(404)
        # noinspection PyUnreachableCode
        db.session.delete(card)
        db.session.commit()
        return

    def post(self,deck_id):
        try:
            front = request.form['front']
            back = request.form['back']
        except KeyError:
            raise BusinessValidationError(400, error_code=error_dict['C2e'][0], error_msg=error_dict['C2e'][1])

        card = db.session.query(Cards).filter(Cards.front == front).first()

        if card:
            raise BusinessValidationError(400, error_code=error_dict['C1e'][0], error_msg=error_dict['C1e'][1])

        new_deck = Cards(deck_id=deck_id, front=front, back=back)
        db.session.add(new_deck)
        db.session.commit()
        return

# =================================== SCORE API =================================== #


class ScoreAPI(Resource):
    def get(self, deck_id):
        user = db.session.query(User_table).filter(User_table.username == session['username']).all()
        for i in user:
            if i.deck_id == deck_id:
                return i.score
        else:
            raise NotFoundError(status_code=404)


    def put(self, deck_id):
        try:
            m = request.form['answer']
            if m == 'right':
                user = db.session.query(User_table).filter(User_table.username == session['username']).all()
                for i in user:
                    if i.deck_id == deck_id:
                        i.score += 1
                        db.session.commit()
            else: pass
        except KeyError:
            raise BusinessValidationError(400,  error_code=error_dict['S1e'][0], error_msg=error_dict['S1e'][1])
        finally:
            return


# =================================== REVIEW API =================================== #

class CardReviewAPI(Resource):
    def get(self, card_id, deck_id):
        card = db.session.query(Cards).filter(Cards.card_id == card_id).first()
        if card.deck_id != deck_id:
            raise NotFoundError(404)
        elif card:
            level = {card.easy: 'Easy',card.good: 'Good', card.hard: 'Hard'}
            j = max(level)
            return f'{j} people found it {level.get(max(level))}'
        return NotFoundError(404)

    def put(self, card_id, deck_id):
        try:
            m = request.form['review']
            card = db.session.query(Cards).filter(Cards.card_id == card_id).first()
            if card.deck_id != deck_id:
                raise NotFoundError(404)
            elif m == 'easy':
                card.easy += 1
            elif m == 'good':
                card.good += 1
            elif m == 'hard':
                card.hard += 1
            db.session.commit()
        except KeyError:
            raise BusinessValidationError(400,  error_code=error_dict['R1e'][0], error_msg=error_dict['R1e'][1])
        finally:
            return

class DeckReviewAPI(Resource):

    def get(self, deck_id):
        level = {'easy': 0, 'hard': 0, 'good': 0}
        deck = db.session.query(Cards).filter(Cards.deck_id == deck_id).all()
        for i in deck:
            level['easy'] += i.easy
            level['hard'] += i.hard
            level['good'] += i.good
        if level['easy'] == level['hard'] == level['good'] == 0:
            return f'No reviews Yet'
        return f'{level.get(max(level))} people found it {max(level)}'




