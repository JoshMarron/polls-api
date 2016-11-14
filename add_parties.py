import json
from models import Party
from polls_api import db
import requests

with open('json_data/parties.json', 'r') as parties_file:  # use local edited version
    parties = json.load(parties_file)

r = requests.get('http://opinionbee.uk/json/types')
types = r.json()

#: :type: dict
leaderdict = types.get("LEAD").get("candidatelist")

for party in parties:
    code = party
    details = parties.get(party)  # Get inner dict

    name = details.get("name")
    colour = details.get("colour")
    text_colour = details.get("textcolor")
    url = details.get("url")
    candidate = leaderdict.get(code)

    party_model = Party(name=name, code=code,
                        colour=colour, text_colour=text_colour, url=url,
                        candidate=candidate)
    db.session.add(party_model)
db.session.commit()
