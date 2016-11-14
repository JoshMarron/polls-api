from polls_api import db
from models import Company, Party, Poll, PollParty
from datetime import datetime
from dateutil import tz
from dateutil import parser
import arrow

import json


with open('json_data/scotland-regional.json', 'r') as westminster_file:
    west_polls = json.load(westminster_file)

for poll in west_polls:
    id = poll
    details = west_polls.get(id)

    # Converts the date to UTC before storing
    date = parser.parse(details.get('date').get('date'))
    timezone = tz.gettz(details.get('date').get('timezone'))
    zone_date = arrow.get(date, timezone)
    utc_date = zone_date.to('UTC')
    utc_date_obj = utc_date.datetime  # This is the one python likes

    # Get other attributes
    title = details.get('type').get('name')
    company_code = details.get('company').get('code')
    client = details.get('client')
    if not client: client = None

    category = details.get('type').get('canonical')
    url = details.get('tablesurl')
    if not url: url = None  # Because url not always there

    company_model = Company.query.get(company_code)
    poll_model = Poll(id=id, date=utc_date_obj, url=url, category=category,
                      title=title, client=client, company_code=company_code)

    parties = details.get('headline')
    for party in parties:
        party_details = parties.get(party)
        print(poll)
        if not party: party = 'OTH'
        score = party_details.get('pct')

        pp_model = PollParty(score=score)
        party_model = Party.query.get(party)
        pp_model.party = party_model
        poll_model.parties.append(pp_model)

    db.session.add(poll_model)
db.session.commit()
