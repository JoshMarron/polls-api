Polls API

Back-end for a lightweight political poll viewing web app, written with Flask. The Flask app exposes an api which is view-agnostic and can be consumed by any front-end setup capable of making calls to it. The api is designed with REST goals in mind and provides easily accessible and understandable URLs.
The Flask app uses the opinionbee.uk polls, parties, types and companies API, found here:
http://opinionbee.uk/api

The app interactes with a PostgreSQL database via SQLAlchemy.
