from flask import Flask
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
import arrow
from config import config

app = Flask(__name__)
app.config.from_object(config.DevConfig)
db = SQLAlchemy(app)
import models
migrate = Migrate(app, db)

CURRENT_CYCLE_START = arrow.get('2015-05-07').datetime

@app.route('/')
@app.route('/polls/current/')
@app.route('/polls/current/<int:page_num>/')
def list_current_polls(page_num=1):
    polls = models.Poll.query.filter(models.Poll.date >= CURRENT_CYCLE_START).order_by(desc(models.Poll.date)).paginate(page_num, 20)
    return flask.jsonify(current_polls=[poll.serialize for poll in polls.items])

@app.route('/parties/')
def list_parties():
    parties = models.Party.query.filter().all()
    return flask.jsonify(party_list=[party.serialize for party in parties])

@app.route('/parties/<party_code>/')
def details_party(party_code):
    party = models.Party.query.get(party_code.upper())
    return flask.jsonify(party.serialize)

@app.route('/parties/<party_code>/polls/')
@app.route('/parties/<party_code>/polls/<int:page_num>/')
def list_party_polls(party_code, page_num=1):
    return_list = []
    party = models.Party.query.get(party_code.upper())
    id_list = [poll.poll_id for poll in party.polls]
    poll_list = models.Poll.query.filter(models.Poll.id.in_(id_list)).order_by(desc(models.Poll.date)).paginate(page_num, 50)
    for poll in poll_list.items:
        return_val = poll.serialize_for_party
        return_val["score"] = models.PollParty.query.get((poll.id, party_code.upper())).score
        return_list.append(return_val)
    return flask.jsonify(return_list)

@app.route('/companies/')
def list_companies():
    companies = models.Company.query.filter().all()
    return flask.jsonify(company_list=[company.serialize for company in companies])

@app.route('/companies/<company_name>/')
def details_company(company_name):
    company = models.Company.query.filter_by(canonical=company_name).one()
    return flask.jsonify(company.serialize)

@app.route('/companies/<company_name>/polls/')
@app.route('/companies/<company_name>/polls/<int:page_num>/')
def list_company_polls(company_name, page_num=1):
    company = models.Company.query.filter_by(canonical=company_name).one()
    polls = company.company_polls.filter().order_by(desc(models.Poll.date)).paginate(page_num, 20)
    return flask.jsonify(company_polls=[poll.serialize for poll in polls.items])

@app.route('/polls/')
@app.route('/polls/<int:page_num>/')
def list_polls(page_num=1):
    polls_page = models.Poll.query.filter().order_by(desc(models.Poll.date)).paginate(page_num, 50)
    polls = polls_page.items
    return flask.jsonify(polls_list=[poll.serialize for poll in polls])

@app.route('/polls/id/<int:poll_id>/')
def details_poll(poll_id):
    poll = models.Poll.query.get_or_404(poll_id)
    return flask.jsonify(poll.serialize)

@app.route('/polls/categories/')
def list_categories():
    categories = []
    polls = models.Poll.query.filter().distinct(models.Poll.category).all()
    for poll in polls:
        categories.append(poll.category)
    return flask.jsonify(categories)

@app.route('/polls/<string:category>/')
@app.route('/polls/<string:category>/<int:page_num>')
def list_category_polls(category, page_num=1):
    polls_page = models.Poll.query.filter_by(category=category).order_by(desc(models.Poll.date)).paginate(page_num, 50)
    return flask.jsonify(category_list=[poll.serialize for poll in polls_page.items])

if __name__ == '__main__':
    app.run(debug=True)
