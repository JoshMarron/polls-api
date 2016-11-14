from polls_api import db
from datetime import datetime

class Company(db.Model):
    code = db.Column(db.String(6), primary_key=True, nullable=False)  # Use this for urls in api
    name = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.String(200), unique=True)
    canonical = db.Column(db.String(40), unique=True, nullable=False)
    company_polls = db.relationship('Poll', backref='company', lazy='dynamic', cascade="all")

    @property
    def serialize(self):
        return {
            "code" : self.code,
            "name" : self.name,
            "url" : self.url,
            "canonical" : self.canonical
        }

class PollParty(db.Model):
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id', ondelete="CASCADE"), primary_key=True)
    party_code = db.Column(db.String(10), db.ForeignKey('party.code', ondelete="CASCADE"), primary_key=True)
    score = db.Column(db.Integer, nullable=False)

    poll = db.relationship("Poll", back_populates="parties")
    party = db.relationship("Party", back_populates="polls")

    @property
    def serialize_party(self):
        return {
            "code" : self.party_code,
            "name" : self.party.name,
            "colour" : self.party.colour,
            "text_colour" : self.party.text_colour,
            "score" : self.score
        }

    @property
    def serialize_polls(self):
        return {
            "poll" : self.poll.serialize_for_party,
            "score" : self.score
        }

class Party(db.Model):
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False, primary_key=True)
    colour = db.Column(db.String(10), nullable=False)
    text_colour = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(200), unique=True)
    candidate = db.Column(db.String(30))  # Name of the candidate for leadership polls
    polls = db.relationship("PollParty", back_populates="party")
    def __repr__(self):
        return self.name

    @property
    def serialize(self):
        return {
            "code" : self.code,
            "name" : self.name,
            "colour" : self.colour,
            "text_colour" : self.text_colour,
            "url" : self.url,
            "candidate" : self.candidate
        }

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    date = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.String)
    category = db.Column(db.String(20), nullable=False)  # called code in json_data, should allow fun separation
    title = db.Column(db.String(200), nullable=False)
    client = db.Column(db.String(100))
    parties = db.relationship("PollParty", back_populates="poll")
    company_code = db.Column(db.String(6), db.ForeignKey('company.code', ondelete="CASCADE"))

    @property
    def serialize_parties(self):
        return [party.serialize_party for party in self.parties]

    @property
    def serialize_company(self):
        return self.company.serialize

    @property
    def serialize(self):
        return {
            "id" : self.id,
            "date" : self.date.isoformat(),
            "url" : self.url,
            "title" : self.title,
            "client" : self.client,
            "company" : self.serialize_company,
            "parties" : self.serialize_parties,
            "category" : self.category
        }

    @property
    def serialize_for_party(self):
        return {
            "id" : self.id,
            "date" : self.date.isoformat(),
            "title" : self.title,
            "client": self.client,
            "url" : self.url,
            "company" : self.serialize_company
        }
