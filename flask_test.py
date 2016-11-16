from polls_api import app, db
import unittest
import models
import arrow
from config import config
import json


class FlaskTests(unittest.TestCase):

    def setUp(self):
        app.config.from_object(config.TestConfig)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_current_cycle_polls(self):

        date1 = arrow.get('2014-10-23').datetime
        date2 = arrow.get('2017-11-24').datetime

        poll1 = models.Poll(id=1, date=date1, url="fe", category="m",
                            title="sometitle", client="someclient")
        poll2 = models.Poll(id=2, date=date2, url="someurl", category="m",
                            title="someothertitle", client="someclient")

        db.session.add(poll1)
        db.session.add(poll2)
        db.session.commit()

        response = self.app.get('/')
        decoded = response.get_data().decode("utf-8")
        response_json = json.loads(decoded)

        # Check we only get the poll dated after the current cycle
        assert len(response_json['current_polls']) == 1
        assert response_json['current_polls'][0]['title'] == "someothertitle"

        # Test for edge case of poll ON the cycle start
        date3 = arrow.get('2015-05-07').datetime
        poll3 = models.Poll(id=3, date=date3, url="someurl", category='n',
                            title="anothertitle", client="someotherclient")

        db.session.add(poll3)
        db.session.commit()

        response = self.app.get('/')
        decoded = response.get_data().decode("utf-8")
        response_json = json.loads(decoded)

        # Check we get both polls dated after the current cycle
        assert len(response_json['current_polls']) == 2

    def test_get_party_polls(self):

        date1 = arrow.get('2014-10-23').datetime
        date2 = arrow.get('2017-11-24').datetime

        poll1 = models.Poll(id=1, date=date1, url="fe", category="m",
                            title="sometitle", client="someclient")
        poll2 = models.Poll(id=2, date=date2, url="someurl", category="m",
                            title="someothertitle", client="someclient")
        party1 = models.Party(name="somename", code="PAR", colour="col",
                              text_colour="tcol", url="someurl")
        poll_party1 = models.PollParty(score=30)
        poll_party2 = models.PollParty(score=25)
        poll_party1.poll = poll1
        poll_party2.poll = poll2
        party1.polls.append(poll_party1)
        party1.polls.append(poll_party2)

        db.session.add(party1)
        db.session.commit()

        response = self.app.get('/parties/par/polls/')
        decoded = response.get_data().decode("utf-8")
        response_json = json.loads(decoded)

        # Check the party has the 2 given polls
        assert len(response_json) == 2

        # Check the scores are in the response
        assert b"30" in response.get_data()
        assert b"25" in response.get_data()

        # Check the entries are correctly sorted by date
        response_date = arrow.get(response_json[0].get('date')).datetime
        assert response_date == date2

        # Check that trying to access a non-existent page throws 404
        response = self.app.get('/parties/par/polls/2/')
        assert response.status_code == 404

    def test_pagination_polls(self):

        date1 = arrow.get('2017-01-01').datetime

        for i in range(1, 500):
            poll = models.Poll(id=i, date=date1, url="someurl", category="m",
                               title="sometitle", client="someclient")
            db.session.add(poll)
        db.session.commit()

        response_page1 = self.app.get('/polls/')
        decoded_page1 = response_page1.get_data().decode('utf-8')
        response_json_page1 = json.loads(decoded_page1)

        # Check we only get 50 responses on page 1
        assert len(response_json_page1['polls']) == 50

        response_page2 = self.app.get('/polls/2/')
        decoded_page2 = response_page2.get_data().decode('utf-8')
        response_json_page2 = json.loads(decoded_page2)

        # Check we only get 50 responses on page 2
        assert len(response_json_page2['polls']) == 50

        # Check the top items of each page are not the same
        top_poll1 = response_json_page1['polls'][0]
        top_poll2 = response_json_page2['polls'][0]

        assert top_poll1 != top_poll2

        # Check that going a page too far returns an error
        response_over_max = self.app.get('/polls/11/')
        assert response_over_max.status_code == 404

    def test_get_company_polls(self):

        date1 = arrow.get('2014-10-23').datetime
        date2 = arrow.get('2017-11-24').datetime

        poll1 = models.Poll(id=1, date=date1, url="fe", category="m",
                            title="sometitle", client="someclient")
        poll2 = models.Poll(id=2, date=date2, url="someurl", category="m",
                            title="someothertitle", client="someclient")
        company = models.Company(code="COM", name="Company", url="someurl",
                                 canonical="company")
        company.company_polls.append(poll1)
        company.company_polls.append(poll2)
        db.session.add(company)
        db.session.commit()

        # Check we get a response
        response = self.app.get('/companies/company/polls/')
        assert response.status_code == 200

        # Check we get two polls for the company
        decoded = response.get_data().decode('utf-8')
        response_json = json.loads(decoded)
        assert len(response_json['polls']) == 2

        # Check they are sorted by date
        response_date = arrow.get(response_json['polls'][0].get('date')).datetime
        assert response_date == date2

        # Check the two polls are the ones we defined
        assert b"someothertitle" in response.get_data()
        assert b"sometitle" in response.get_data()

    def test_list_parties_for_poll(self):

        date1 = arrow.get('2017-01-01').datetime
        poll1 = models.Poll(id=1, date=date1, url="fe", category="m",
                            title="sometitle", client="someclient")
        party1 = models.Party(name="party1", code="PAR1", colour="col",
                              text_colour="tcol", url="someurl")
        party2 = models.Party(name="party2", code="PAR2", colour="cool",
                              text_colour="tcol", url="someurl1")
        party3 = models.Party(name="party3", code="PAR3", colour="col",
                              text_colour="tcol", url="someurl2")
        pp1 = models.PollParty(score=30)
        pp2 = models.PollParty(score=20)
        pp3 = models.PollParty(score=50)
        pp1.party = party1
        pp2.party = party2
        pp3.party = party3
        poll1.parties.append(pp1)
        poll1.parties.append(pp2)
        poll1.parties.append(pp3)

        db.session.add(poll1)
        db.session.commit()

        # Check the party is there
        response = self.app.get('/polls/id/1/')
        assert response.status_code == 200

        # Check the scores are there
        assert b'30' in response.get_data()
        assert b'20' in response.get_data()
        assert b'50' in response.get_data()

        decoded = response.get_data().decode('utf-8')
        response_json = json.loads(decoded)

        # Check we have the expected number of parties
        assert len(response_json['parties']) == 3

        parties = []
        for party in response_json['parties']:
            parties.append(party.get('code'))

        assert "PAR1" in parties
        assert "PAR2" in parties
        assert "PAR3" in parties

    def test_list_categories(self):

        date1 = arrow.get('2014-10-23').datetime
        for i in range(1, 250):
            poll = models.Poll(id=i, date=date1, url="someurl", category="m",
                               title="sometitle", client="someclient")
            db.session.add(poll)
        for i in range(251, 500):
            poll = models.Poll(id=i, date=date1, url="someurl", category="n",
                               title="someothertitle", client="someotherclient")
            db.session.add(poll)
        db.session.commit()

        response = self.app.get('polls/categories/')
        assert response.status_code == 200
        decoded = response.get_data().decode('utf-8')
        response_json = json.loads(decoded)

        assert len(response_json) == 2
        assert "m" in response_json
        assert "n" in response_json

    def test_get_specific_poll(self):

        date1 = arrow.get('2014-10-23').datetime
        date2 = arrow.get('2017-11-24').datetime

        poll1 = models.Poll(id=1, date=date1, url="fe", category="m",
                            title="sometitle", client="someclient")
        poll2 = models.Poll(id=2, date=date2, url="someurl", category="m",
                            title="someothertitle", client="someclient")

        db.session.add(poll1)
        db.session.add(poll2)
        db.session.commit()

        response = self.app.get('/polls/id/1/')
        assert response.status_code == 200
        decoded = response.get_data().decode('utf-8')
        response_json = json.loads(decoded)
        assert response_json['title'] == "sometitle"

        response = self.app.get('/polls/id/2/')
        assert response.status_code == 200
        decoded = response.get_data().decode('utf-8')
        response_json = json.loads(decoded)
        assert response_json['title'] == "someothertitle"

        response = self.app.get('/polls/id/3/')
        assert response.status_code == 404



if __name__ == '__main__':
    unittest.main()
