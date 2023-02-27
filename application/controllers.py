from flask import request, render_template, redirect, url_for, g
from flask import current_app as app
from application.models import *
from flask import session
from random import choice
from  datetime import datetime
from application.card_controllers import *

# ================================ LOGIN PAGE / LOGOUT / SESSION CHECK =================================== #

dt_string = 'Not visited yet :('

@app.route("/", methods=["GET", "POST"])
def login_page():
    if not g.user:
        if request.method == 'POST':
            session['username']= request.form["username"]
            user = User.query.filter_by(username=session['username']).first()
            if user:
                return redirect(url_for("dashboard"))
            session.pop('username', None)
            return redirect(url_for('login_page'))
        return render_template("login-page.html")
    return redirect(url_for('dashboard'))


@app.before_request
def before_request():
    g.user = None
    if 'username' in session:
        g.user = session['username']


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


# ============================================ DASHBOARD =========================================#


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if g.user:
        if request.method == 'GET':
            m = User.query.filter_by(username=session["username"]).first()
            n = User_table.query.filter_by(username=session["username"]).all()
            p = Decks.query.all()
            return render_template("dashboard.html", m=m, n=n, p=p, username=session["username"])
        # add js alert fro logout everywhere
    return redirect(url_for("login_page"))

# ========================== DECK CONTROLLERS USING DECK API ============================= #


@app.route("/dashboard/<deck_id>", methods=["GET", "POST"])
def deck_page(deck_id):
    if g.user:
        if request.method == 'GET':
            n = DeckAPI().get(deck_id)
            m = ScoreAPI().get(deck_id)
            o = DeckReviewAPI().get(deck_id)
            return render_template("deck.html", n=n, m=m, o=o, dt_string=dt_string)
    return redirect(url_for("login_page"))


@app.route('/dashboard/add_deck', methods=["GET", "POST"])
def new_deck():
    if g.user:
        if request.method == 'GET':
            p = Decks.query.all()
            return render_template('add-deck.html', p=p)
        if request.method == 'POST':
            m = DeckAPI().post()
            return redirect(url_for("deck_page", deck_id=m))
    return redirect(url_for('login_page'))


@app.route('/dashboard/add_deck/<deck_id>')
def add_deck(deck_id):
    if g.user:
        m = User_table.query.filter_by(username=session["username"]).all()
        p = None
        for i in m:
            if i.deck_id == deck_id:
                p=i
        if p is None:
            user_deck = User_table(username=session['username'], deck_id=deck_id, score=0)
            db.session.add(user_deck)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for("login_page"))


@app.route('/dashboard/<deck_id>/edit', methods=["GET","POST"] )
def edit_deck(deck_id):
    if g.user:
        if request.method == 'GET':
            n = Decks.query.filter_by(deck_id=deck_id).first()
            return render_template('edit-deck.html',n=n)
        elif request.method == 'POST':
            DeckAPI().put(deck_id)
            return redirect(url_for('deck_page', deck_id=deck_id))
    return redirect(url_for("login_page"))


@app.route('/dashboard/<string:deck_id>/remove')
def remove_deck(deck_id):
    if g.user:
        DeckAPI().delete(deck_id)
        return redirect(url_for('dashboard'))

# ============================= CARD CONTROLLERS USING CARD API =================================== #

@app.route('/dashboard/<string:deck_id>/study',methods=["GET","POST"])
def card_page(deck_id):
    if g.user:
        if request.method == 'GET':
            m = Cards.query.filter_by(deck_id=deck_id).all()
            try: 
                card_id = choice(m).card_id
            except:
                return redirect(url_for('deck_page',deck_id=deck_id))
            a = CardAPI().get(deck_id, card_id)
            n = Decks.query.filter_by(deck_id=deck_id).first()
            f = CardReviewAPI().get(card_id, deck_id)
            return render_template("card_page.html", m=a, n=n, f=f)
        ScoreAPI().put(deck_id)
        m = Cards.query.filter_by(deck_id=deck_id).all()
        card_id = choice(m).card_id
        a = CardAPI().get(deck_id, card_id)
        n = Decks.query.filter_by(deck_id=deck_id).first()
        now = datetime.now()
        global dt_string
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f = CardReviewAPI().get(card_id, deck_id)
        return render_template("card_page.html", m=a, n=n, f=f)
    return redirect(url_for('login_page'))


@app.route('/dashboard/<string:deck_id>/study/<string:card_id>/delete')
def delete_card(deck_id, card_id):
    if g.user:
        CardAPI().delete(deck_id, card_id=card_id)
        return redirect(url_for('card_page', deck_id=deck_id))


@app.route('/dashboard/<string:deck_id>/study/<string:card_id>/edit', methods=["GET","POST"])
def edit_card(deck_id,card_id):
    if g.user:
        if request.method == 'GET':
            n = Decks.query.filter_by(deck_id=deck_id).first()
            m = Cards.query.filter_by(card_id=card_id).first()
            return render_template('edit-card.html',n=n,m=m)
        if request.method == 'POST':
            CardAPI().put(deck_id,card_id)
            return redirect(url_for('card_page', deck_id=deck_id))


@app.route('/dashboard/<string:deck_id>/study/add', methods=["GET","POST"])
def add_card(deck_id):
    if g.user:
        if request.method == 'GET':
            n = Decks.query.filter_by(deck_id=deck_id).first()
            return render_template('add-card.html', n=n)
        if request.method == 'POST':
            CardAPI().post(deck_id)
            return redirect(url_for("card_page", deck_id=deck_id))
    return redirect(url_for('login_page'))


